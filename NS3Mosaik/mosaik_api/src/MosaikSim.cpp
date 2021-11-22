/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2019 Evandro de Souza
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 * Author:  Evandro de Souza <evandro@ualberta.ca>
 * Date:    2019.05.25
 * Company: University of Alberta/Canada - Computing Science
 *
 * Author:  Amrinder S. Grewal <asgrewal@ualberta.ca>
 * Date:    2020.05.09
 * Company: University of Alberta/Canada - Computing Science
 */

#include "MosaikSim.h"


MosaikSim::MosaikSim(std::string varargin, NS3Netsim *obj) {
  std::cout << "Starting MosaikSim class with varargin: " << varargin << std::endl;

  //--- Gets server from mosaik and verify if it has two parts
  assert(!varargin.empty() and varargin.find(':'));

  //--- get NS3 object
  objNetsim = obj;

  //--- initialize Mosaik commands map
  initMosaikCommands();

  //--- split host and port
  AddrPort srvAP = parseAddress(varargin);
  host = srvAP.host;
  port = srvAP.port;

  //--- Initial verbose setting (0 = no message)
  verbose = 0;

  //--- create socket
  openSocket();

  //--- start the mainLoop
  stopServer = false;
  startMainLoop();
}


MosaikSim::~MosaikSim() {
  stopMainLoop();
  close(sock);
}


void
MosaikSim::initMosaikCommands(void)
{
  mapMosaikCommands["init"] = cmdInit;
  mapMosaikCommands["create"] = cmdCreate;
  mapMosaikCommands["setup_done"] = cmdSetup_done;
  mapMosaikCommands["step"] = cmdStep;
  mapMosaikCommands["get_data"] = cmdGet_data;
  mapMosaikCommands["stop"] = cmdStop;
  mapMosaikCommands["get_progress"] = cmdGet_progress;
  mapMosaikCommands["get_related_entities"] = cmdGet_related_entities;
  mapMosaikCommands["set_data"] = cmdSet_data;
  mapMosaikCommands["set_next"] = cmdSet_next;
}


AddrPort
MosaikSim::parseAddress(std::string varargin)
{
  AddrPort srv;

  size_t pos = varargin.find(':');
  srv.host = varargin.substr(0, pos);
  srv.port = stoi(varargin.substr(pos + 1));

  assert(!srv.host.empty());
  assert(is_number(varargin.substr(pos + 1)));

  return srv;
}


bool
MosaikSim::is_number(const std::string& s)
{
  return !s.empty() && std::find_if(s.begin(),
                                    s.end(), [](char c) { return !std::isdigit(c); }) == s.end();
}


void
MosaikSim::openSocket(void) {

  std::cout << "MosaikSim::openSocket" << std::endl;

  int result = (sock = socket(AF_INET, SOCK_STREAM, 0));

  if (result < 0) {
      throw std::runtime_error("MosaikSim::openSocket Could not open socket");
    }

  //--- open TCP connection
  memset(&serv_addr, '0', sizeof(serv_addr));
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_addr.s_addr = inet_addr(host.c_str());
  serv_addr.sin_port = htons((uint16_t) port);

  result = connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr));

  if (result < 0) {
      throw std::runtime_error("MosaikSim::openSocket TCP connection failed");
    }
}


void MosaikSim::startMainLoop(void) {
  mainLoop();
}


void MosaikSim::stopMainLoop(void) {
  stopServer = true;
}


void MosaikSim::mainLoop(void) {
  if (verbose > 1)
    std::cout << "MosaikSim::mainLoop" << std::endl;

  std::string result;
  int currentMsgId;
  std::string messages;
  Json::Value jsonMessage;

  while (!stopServer) {
      try {
          //--- reset the mainLoop operation result
          mosaikLastMsgOp = SUCCESS;

          //--- Read Messages form the Socket
          messages = readSocket();

          //--- Deserialize the messages and get message Id
          jsonMessage = deserialize(messages, currentMsgId);

          //--- Select command received, forward to appropriate method, and
          //--- get the result of the command execution
          result = simSocketReceivedRequest(jsonMessage);

          //--- Serialize and write the response
          result = serialize(result, mosaikLastMsgOp, currentMsgId);
          send(sock, result.c_str(), result.size(),0);

          if (verbose > 1)
            std::cout << "MosaikSim::mainLoop ***** MSG SENT !! *****" << std::endl;
        }
      catch (std::exception& e)
        {
          std::cout << e.what() << std::endl;
        }
    }
}


std::string
MosaikSim::readSocket(void) {
  if (verbose > 1)
    std::cout << "MosaikSim::readSocket" << std::endl;

  std::string msgs;
  char buff[MAXRECV];
  uint32_t nBytes   = 0;
  uint32_t p_buffer = 0;
  char header[4];

  //--- get first packet to discover Mosaik message total size
  nBytes = read(sock , buff, MAXRECV);
  for (int i = 0; i < 4; i++)
    header[i] = buff[i];

  if (verbose > 3) {
      std::cout << "Header:";
      for (int i = 0; i < 4 ; i++) {printf(" 0x%02X", buff[i]);}
      cout << endl;
    }

  //--- get total message size
  uint32_t lenMsg = ( ((header[0] << 24) & 0xFF000000) | ((header[1] << 16) & 0x00FF0000) | \
			            ((header[2] <<  8) & 0x0000FF00) | ((header[3] <<  0) & 0x000000FF) );

  //--- Three cases:
  //--- 1) transmission with error
  if( nBytes < 0) {
      perror("MosaikSim::readSocket Message received with error");
      memset(buffer, 0, sizeof(buffer));
      nBytes = 0;
    }

  //--- 2) message completed into a single transmission
  if ( nBytes  > lenMsg ) {
      if (verbose > 2)
        std::cout << "MosaikSim::readSocket Pkt size rcv = " << nBytes << " Msg size Header = " <<  lenMsg << std::endl;

      memcpy(&buffer, buff, nBytes);
    }

  //--- 3) message split into several transmissions
  if ( nBytes  < lenMsg ) {
      if (verbose > 2)
        std::cout << "MosaikSim::readSocket Pkt size rcv = " << nBytes << " Msg size Header = " <<  lenMsg << std::endl;

      memcpy(&buffer, buff, nBytes);
      p_buffer = nBytes;

      do {
          memset(&buff, 0, MAXRECV);
          nBytes = read(sock, buff, MAXRECV);
          if (nBytes > 0) {

              memcpy(&(buffer[p_buffer]), buff, nBytes);
              p_buffer += nBytes;

              if (verbose > 2)
                cout << "MosaikSim::readSocket p_buffer = " << p_buffer << " nBytes = " << nBytes << endl;
            }

        } while (nBytes > 0 && p_buffer < lenMsg);

      nBytes = p_buffer;

    }

  if (verbose > 2)
    cout << "MosaikSim::readSocket "
         << " FINAL: p_buffer = " << p_buffer
         << " nBytes = " << nBytes
         << " lenMsg = " << lenMsg
         << endl << endl;

  if (verbose > 1)
    std::cout << "MosaikSim::readSocket socket read! Bytes: " << nBytes << std::endl;

  if (verbose > 2) {
      printMsg(buffer, nBytes);
    }

  msgs = splitRequest(nBytes);

  return msgs;
}


//--- This function is necessary if there is multiple messages in
//--- the buffer. It might be necessary split and reconstruct them.
//--- For the time being, we assume that there is only one message in the buffer
std::string
MosaikSim::splitRequest(int bufsize) {
  if (verbose > 1)
    std::cout << "MosaikSim::splitRequest" << std::endl;

  if (verbose > 2) {
      std::cout << "MosaikSim::splitRequest bufsize: " << bufsize << std::endl;
    }

  std::string msgs;

  //--- Extract the reader from buffer to msgs string
  msgs.append(buffer, bufsize);

  if (verbose > 2)
    std::cout << "MosaikSim::splitRequest msgs" << msgs << std::endl;

  //--- remove the first four bytes (message header)
  msgs.erase(msgs.begin(), msgs.begin()+4);

  if (verbose > 1)
    std::cout << "MosaikSim::splitRequest msgs without header " << msgs << std::endl;

  return msgs;
}


Json::Value
MosaikSim::deserialize(std::string payload, int& currentMsgId) {
  if (verbose > 1)
    std::cout << "MosaikSim::deserialize" << std::endl;

  if (verbose > 2)
    std::cout << "MosaikSim::deserialize payload: " << payload << std::endl;

  Json::Reader reader;
  Json::Value obj;

  bool result = reader.parse(payload, obj);

  //--- parsing unsuccessful
  if(!result) {
      std::cout << "MosaikSim::deserialize Parsing not successful!" << std::endl;
      std::cout << "MosaikSim::deserialize Message - SIZE: " << payload.size() << "  Content: " << payload << std::endl;

      //--- parsing successful
    } else {

      currentMsgId = (obj[1]).asInt();
      mosaikLastMsgId = currentMsgId;

      if (verbose > 1)
        std::cout << "MosaikSim::deserialize "
                  << "MessageId: " << currentMsgId
                  << " Type: "     << obj[0].asInt()
                  << " Content: "  << obj[2] << std::endl;

    }

  return obj[2];
}


std::string
MosaikSim::simSocketReceivedRequest(Json::Value request)
{
  if (verbose > 1)
    std::cout << "MoisaikSim::simSocketReceivedRequest" << std::endl;

  std::string result;
  std::string func;
  Json::Value args;
  Json::Value kwargs;

  func.append((request[0]).asString());
  args   = request[1];
  kwargs = request[2];

  if (verbose > 2)
    std::cout << "MoisaikSim::simSocketReceivedRequest process command: " << func << std::endl;

  if (request.size() > 3) {
      std:: cout << "Request has more than 3 arguments, these will be ignored" << std::endl;
    }

  //--- Process request according to each command
  switch(mapMosaikCommands[func])
    {
      case cmdInit:
        result = init(args, kwargs);
      break;
      case cmdCreate:
        result = create(args, kwargs);
      break;
      case cmdSetup_done:
        result = setup_done();
      break;
      case cmdStep:
        result = step(args, kwargs);
      break;
      case cmdGet_data:
        result = get_data(args, kwargs);
      break;
      case cmdSet_next:
        result = set_next(args, kwargs);
      break;
      case cmdStop:
        result = stop();
      std::exit(0);
      break;
      default:
        std::cout << func << " is an invalid/not implemented Mosaik command. Ignored!" << std::endl;
      break;
    }

  if (verbose > 1)
    std::cout << "MoisaikSim::simSocketReceivedRequest result: " << result << std::endl;

  return result;
}


std::string
MosaikSim::init(Json::Value args, Json::Value kwargs) {

  std::string result;
  std::string param;

  mosaikSid = args[0].asString();

  if (verbose > 1)
    std::cout << "MoisaikSim::init mosaikSid: " << mosaikSid << std::endl;

  //--- process each parameter
  for(Json::Value::const_iterator item = kwargs.begin() ; item != kwargs.end(); item++)
    {
      param = (item.key()).asString();

      if (verbose > 2)
        std::cout << "MoisaikSim::init param: " << item.key() << " : " << *item << std::endl;

      if (strcmp(param.c_str(), "model_name") == 0)
        {
          netsimProp.model_name.append((*item).asString());
        }
      else if (strcmp(param.c_str(), "eid_prefix") == 0)
        {
          netsimProp.eid_prefix.append((*item).asString());
        }
      else if (strcmp(param.c_str(), "instance_name") == 0)
        {
          netsimProp.instance_name.append((*item).asString());
        }
      else if (strcmp(param.c_str(), "start_time") == 0)
        {
          netsimProp.start_time = (*item).asDouble();
        }
      else if (strcmp(param.c_str(), "stop_time") == 0)
        {
          netsimProp.stop_time = (*item).asDouble();
        }
      else if (strcmp(param.c_str(), "random_seed") == 0)
        {
          netsimProp.random_seed = (*item).asDouble();
        }
      else if (strcmp(param.c_str(), "time_resolution") == 0)
        {
          netsimProp.seconds_per_mosaik_timestep = (*item).asDouble();
        }
      else if (strcmp(param.c_str(), "step_size") == 0)
        {
          netsimProp.step_size = (*item).asDouble();
        }
      else if (strcmp(param.c_str(), "appcon_file") == 0)
        {
          netsimProp.appcon_file = (*item).asString();
          vecNetSimConn = readAppConnectionsFile (netsimProp.appcon_file);
        }
      else if (strcmp(param.c_str(), "adjmat_file") == 0)
        {
          netsimProp.adjmat_file = (*item).asString();
        }
      else if (strcmp(param.c_str(), "coords_file") == 0)
        {
          netsimProp.coords_file = (*item).asString();
        }
      else if (strcmp(param.c_str(), "verbose") == 0)
        {
          netsimProp.verbose = (*item).asInt();
          verbose = netsimProp.verbose;
        }
      else if (strcmp(param.c_str(), "linkRate") == 0)
        {
          netsimProp.linkRate = (*item).asString();
        }
      else if (strcmp(param.c_str(), "linkDelay") == 0)
        {
          netsimProp.linkDelay = (*item).asString();
        }
      else if (strcmp(param.c_str(), "linkErrorRate") == 0)
        {
          netsimProp.linkErrorRate = (*item).asString();
        }
      else if (strcmp(param.c_str(), "tcpOrUdp") == 0)
        {
          netsimProp.tcpOrUdp = (*item).asString();
        }
      else {
          std::cout << "Unknown init parameter" << item.key() << std::endl;
          mosaikLastMsgOp = FAILURE;
        }
    }

  //--- Initialize NS3 class
  objNetsim->init(netsimProp.adjmat_file,
                  netsimProp.coords_file,
                  netsimProp.appcon_file,
                  netsimProp.linkRate,
                  netsimProp.linkDelay,
                  netsimProp.linkErrorRate,
                  netsimProp.start_time,
                  netsimProp.verbose,
                  netsimProp.tcpOrUdp);


  //--- initialize Meta model
  mosaikMeta  = TransporterMeta;

  result = meta();

  if (verbose > 1)
    std::cout << "MoisaikSim::init result: " << result << std::endl;

  return result;
}


std::string
MosaikSim::meta(void)
{
  if (verbose > 1)
    std::cout << "MosaikSim::meta" << std::endl;

  std::string meta;
  Json::Value obj;
  Json::StreamWriterBuilder wbuilder;

  obj["api_version"] = mosaikMeta.api_version;
  obj["type"] = mosaikMeta.type;
  obj["models"][mosaikMeta.model]["public"] = mosaikMeta.props->access;

  int attr_size = sizeof(mosaikMeta.props->attrs)/sizeof(mosaikMeta.props->attrs[0]);
  for (int i = 0; i < attr_size; i++) {
      if (!mosaikMeta.props->attrs[i].empty()) {
          obj["models"][mosaikMeta.model]["attrs"].append(mosaikMeta.props->attrs[i]);
        }
    }

  int param_size = sizeof(mosaikMeta.props->params)/sizeof(mosaikMeta.props->params[0]);
  for (int i = 0; i < param_size; i++) {
      if (!mosaikMeta.props->params[i].empty()) {
          obj["models"][mosaikMeta.model]["params"].append(mosaikMeta.props->params[i]);
        }
    }

  int methods_size = sizeof(mosaikMeta.extra_methods)/sizeof(mosaikMeta.extra_methods[0]);
  for (int i = 0; i < methods_size; i++) {
      if (!mosaikMeta.extra_methods[i].empty()) {
          obj["extra_methods"].append(mosaikMeta.extra_methods[i]);
        }
    }

  meta = Json::writeString(wbuilder, obj);

  if (verbose > 1)
    std::cout << "MosaikSim::meta META = " << meta << std::endl;

  return meta;
}


std::string
MosaikSim::create(Json::Value args, Json::Value kwargs)
{
  std::string result;
  std::string entity;

  mosaikNum      = args[0].asInt();
  mosaikSimModel = args[1].asString();

  if (verbose > 1)
    std::cout << "MosaikSim::create mosaikNum: " << mosaikNum << " - mosaikSimModel: " << mosaikSimModel << std::endl;

  //--- Store simulator parameters
  for (auto const& key : kwargs.getMemberNames()) {
      netsimParams[key] = (kwargs[key]).asString();
    }

  if (verbose > 2) {
      std::map<std::string, std::string>::iterator it;
      std::cout << "MosaikSim::create netsimParams ";
      for ( it = netsimParams.begin(); it != netsimParams.end(); it++ ) {
          std::cout << it->first
                    << ':'
                    << it->second
                    << " ";
        }
      std::cout << std::endl;
    }

  //--- create source and destination sockets in NS3
  objNetsim->create(netsimParams["src"], netsimParams["dst"]);

  //--- generate eid
  std::string eid = netsimProp.eid_prefix;
  eid.append(netsimParams["src"]);
  eid.append("-");
  eid.append(netsimParams["dst"]);

  if (verbose > 1) {
      std::cout << "MosaikSim::create eid: " << eid << std::endl;
    }

  //--- create instances of the simulator
  netsimEntities[eid] = std::make_pair(netsimParams["src"], netsimParams["dst"]);

  result.append("[");
  result.append(dscrListForEntities(eid));
  result.append("]");

  if (verbose > 1) {
      std::cout << "MosaikSim::create result: " << result << std::endl;
    }

  return result;
}


std::string
MosaikSim::dscrListForEntities(std::string eid)
{
  if (verbose > 1)
    std::cout << "MosaikSim::dscrListForEntities" << std::endl;

  std::string dscrList;
  Json::Value obj;
  Json::StreamWriterBuilder wbuilder;

  obj["type"] = mosaikSimModel;
  obj["eid"]  = eid;

  dscrList = Json::writeString(wbuilder, obj);

  if (verbose > 2)
    std::cout << "MosaikSim::dscrList dscrList = " << dscrList << std::endl;

  return dscrList;
}


std::string
MosaikSim::setup_done(void)
{
  if (verbose > 1)
    std::cout << "MosaikSim::setup_done" << std::endl;

  return "null";
}


std::string
MosaikSim::step(Json::Value args, Json::Value kwargs)
{
  //---
  //--- Calculate the next step time
  //---
  std::string time_next_step;
  mosaikTime = args[0].asUInt64();
  uint64_t maxAdvance = args[2].asUInt64();
  time_next_step = std::to_string(maxAdvance);

  if (verbose > 1) {
      std::cout << "MosaikSim::step time, args = " << mosaikTime << "\n" << args << std::endl;
    }

  //---
  //--- Extract input data received from Mosaik and insert into a map
  //---
  struct rcvData {
      std::string val_S;
      std::string val_D;
      std::string val_V;
      std::string val_T;
  };
  std::map<std::string, rcvData> mapRcvData;
  std::map<std::string, rcvData>::iterator itMapRcvData;
  std::string localSimulatorInstance;

  std::vector<std::string> lsi = (args[1]).getMemberNames();
  for ( auto lsi_i = lsi.begin(); lsi_i != lsi.end(); lsi_i++ ){
      localSimulatorInstance = *lsi_i;

      if(verbose > 3) {
          std::cout << "MosaikSim::step localSimulatorInstance: " << localSimulatorInstance << std::endl;
        }

      //--- interact through local variables
      rcvData rcvMsg;
      std::string localVariable;

      std::vector<std::string> sv = (args[1][localSimulatorInstance]).getMemberNames();

      for ( auto sv_i = sv.begin(); sv_i != sv.end(); sv_i++ ){
          localVariable = *sv_i;

          //--- empty variable for new round
          rcvMsg = {};

          //--- interact through local instances variables remote instances
          std::string remoteSimulatorInstance;
          std::string attr_value;
          Json::FastWriter fastWriter;

          std::vector<std::string> rsi = (args[1][localSimulatorInstance][localVariable]).getMemberNames();
          for ( auto rsi_i = rsi.begin(); rsi_i != rsi.end(); rsi_i++ ){
              remoteSimulatorInstance = *rsi_i;
              attr_value = fastWriter.write((args[1][localSimulatorInstance][localVariable][remoteSimulatorInstance]));

              if (verbose > 2) {
                  std::cout << "MosaikSim::step Received from Mosaik: "
                            << localSimulatorInstance << " - "
                            << localVariable << " - "
                            << remoteSimulatorInstance << " - "
                            << attr_value << std::endl;
                }

              //--- verify if entry for the current remoteSimulatorInstance already exist
              //--- if not, create new entry
              itMapRcvData = mapRcvData.find(remoteSimulatorInstance);
              if (itMapRcvData == mapRcvData.end()) {
                  mapRcvData[remoteSimulatorInstance] = rcvMsg;
                }

              //--- assign the iterator with the position of the entry
              //--- and assign the values
              itMapRcvData = mapRcvData.find(remoteSimulatorInstance);
              if (itMapRcvData != mapRcvData.end())
                {
                  if(localVariable.compare("v") == 0) {
                      (*itMapRcvData).second.val_V = attr_value;
                    } else if( localVariable.compare("t") == 0) {
                      (*itMapRcvData).second.val_T = attr_value;
                    }
                  std::pair<std::string, std::string> pair = netsimEntities[localSimulatorInstance];
                  (*itMapRcvData).second.val_S = pair.first;
                  (*itMapRcvData).second.val_D = pair.second;
                }

            } //--- remote instances

        } //--- local variables

    } //--- local instances

  //---
  //--- Insert data from map into NS3
  //---
  if (verbose > 1)
    {
      std::cout << "MosaikSim::step Number of Entries for network simulator: " << mapRcvData.size() << std::endl;
    }

  for ( itMapRcvData = mapRcvData.begin(); itMapRcvData != mapRcvData.end(); itMapRcvData++ )
    {
      if (verbose > 1)
        {
          std::cout << "MosaikSim::step NS3_SCHEDULE(src=" << (*itMapRcvData).second.val_S
                    << ", dst="  << (*itMapRcvData).second.val_D
                    << ", val_V="  << (*itMapRcvData).second.val_V
                    << ", time=" << (*itMapRcvData).second.val_T
                    << ")" << std::endl;
        }

      //--- do not insert packet with null value in NS3
      if (((*itMapRcvData).second.val_V).compare("") != 0 &&
          ((*itMapRcvData).second.val_V).find("null") > ((*itMapRcvData).second.val_V).length() &&
          ((*itMapRcvData).second.val_S).compare("") != 0 &&
          ((*itMapRcvData).second.val_D).compare("") != 0 &&
          ((*itMapRcvData).second.val_T).compare("") != 0 &&
          ((*itMapRcvData).second.val_T).find("null") > ((*itMapRcvData).second.val_T).length() )
        {

          if (verbose > 1)
            {
              std::cout << "MosaikSim::step NS3_SCHEDULE(src=" << (*itMapRcvData).second.val_S
                        << ", dst="   << (*itMapRcvData).second.val_D
                        << ", val_V=" << (*itMapRcvData).second.val_V
                        << ", time="  << (*itMapRcvData).second.val_T
                        << ")" << std::endl;
            }

          double currentNS3Time  = objNetsim->getCurrentTime();
          if (currentNS3Time < stod((*itMapRcvData).second.val_T))
            {
              objNetsim->schedule((*itMapRcvData).second.val_S,
                                  (*itMapRcvData).second.val_D,
                                  (*itMapRcvData).second.val_V,
                                  (*itMapRcvData).second.val_T);
            } else {
              std::cout << "MosaikSim::step ROLLBACK TIME !! ("
                        << (*itMapRcvData).second.val_S
                        << "->"
                        << (*itMapRcvData).second.val_D
                        << ") NS3 Time: " << currentNS3Time
                        << " val_T: " << (*itMapRcvData).second.val_T
                        << std::endl;
            }
        }
    }


  //---
  //--- Execute NS3 until time of the next NS3 step
  //---
  if (verbose > 1) {
      std::cout << "MosaikSim::step NS3_RUNUNTIL(time = " << time_next_step << ")" << std::endl;
    }

  //--- Get the next event time ("null" if no events)
  time_next_step = objNetsim->runUntil(mosaikTime, time_next_step);

  //---
  //--- Execute set_data to send sent new results asynchronously
  //--- If used, need to be rewritten to decide who will extract data from NS3
  //---
  //set_data();

  //--- End of step execution. Return time of next step
  //--- This is the look ahead and is not supposed to be executed yet
  //--- The output data is made available in the appropriate step

  if (verbose > 1) {
      std::cout << "MosaikSim::step time_next_step = " << time_next_step << std::endl;
    }

  return time_next_step;
}


std::string
MosaikSim::get_data(Json::Value args, Json::Value kwargs)
{
  if (verbose > 0) {
      Json::FastWriter fastWriter;
      std::string output = fastWriter.write(args);
      std::cout << "MosaikSim::get_data INPUT = " << args << std::endl;
    }

  Json::Value obj;
  Json::Value objRes;
  Json::StreamWriterBuilder wbuilder;
  std::string result;

  std::string val_s;
  std::string val_d;
  std::string val_v;
  std::string val_t;

  std::pair<std::string, std::string> keyOut;
  std::pair<std::string, std::string> valOut;

  obj = args[0];

  //--- clear receiver buffer to avoid to re-send data to the
  //--- next simulator
  mapGetData.clear();

  //--- get local simulator instances
  std::vector<std::string> lsiList = args[0].getMemberNames();
  if (verbose > 2)
    {
      for ( auto lsi_i = lsiList.begin(); lsi_i != lsiList.end(); lsi_i++ ){
          std::cout << "MosaikSim::get_data LSI = " << *lsi_i << std::endl;
        }
    }

  //--- check if NS3 output buffer is not empty and get all data
  if (objNetsim->checkEmptyDataOutput() == 1)
    {
      if (verbose > 2)
        std::cout << "MosaikSim::get_data NO output data on NS3 !! " << std::endl;

      //--- there something in the buffer, retrieve to MosaikSim
    } else {
      if (verbose > 2)
        std::cout << "MosaikSim::get_data NS3 Out-buffer size: " << objNetsim->getSizeDataOutput() <<  std::endl;

      while (objNetsim->getSizeDataOutput() > 0)
        {
          objNetsim->get_data(val_s, val_d, val_v, val_t);

          if (verbose > 2)
            {
              std::cout << "MosaikSim::set_data --OUT from NS3-- "
                        << "Current Time: " << mosaikTime
                        << " val_s = " << val_s
                        << " val_d = " << val_d
                        << "\n val_v = " << val_v
                        << " val_t = " << val_t
                        << std::endl;
            }

          //--- insert data in another buffer
          keyOut = std::make_pair(val_s, val_d);
          valOut = std::make_pair(val_v, val_t);
          mapGetData[keyOut] = valOut;
        }
    }

  //--- for each data request (remote simulator instance [RSI])
  //--- verify if there is data on buffer
  for (auto lsi_i = lsiList.begin(); lsi_i != lsiList.end(); lsi_i++ )
    {
      if (verbose > 2)
        std::cout << "MosaikSim::get_data get data from: " << *lsi_i << std::endl;

      //---
      //--- get src and dst from local instance
      //---
      std::string attr;
      const char delim_tr = '_';
      const char delim_ds = '-';
      std::vector<std::string> out;
      std::vector<std::string>::iterator it;
      std::string pair_name;
      std::string src;
      std::string dst;

      attr = *lsi_i;
      tokenize(attr, delim_tr, out);
      it = out.begin(); ++it;
      pair_name = (*it);

      if (verbose > 2)
        std::cout << "MosaikSim::get_data pair_name: " << pair_name << std::endl;

      attr = pair_name;
      out.clear();
      tokenize(attr, delim_ds, out);
      it = out.begin();
      src = *it;
      ++it;
      dst = *it;

      if (verbose > 2)
        std::cout << "MosaikSim::get_data src: " << src << " dst: " << dst << std::endl;

      //---
      //--- make pair and verify if data exist in mapGetData
      //---
      keyOut = make_pair(src, dst);
      if ( mapGetData.find(keyOut) == mapGetData.end() ) {
          if (verbose > 2)
            std::cout << "MosaikSim::get_data No element in mapGetData " << std::endl;
          //objRes[*lsi_i]["v"] = "None";
          //objRes[*lsi_i]["t"] = "None";
        } else {
          if (verbose > 2)
            std::cout << "MosaikSim::get_data Element found in mapGetData " << std::endl;
          valOut = mapGetData[keyOut];
          objRes[*lsi_i]["v"] = valOut.first;
          objRes[*lsi_i]["t"] = stod(valOut.second);
        }

      if (verbose > 2)
        std::cout << "MosaikSim::get_data objRes: " << objRes << std::endl;
    }

  result = Json::writeString(wbuilder, objRes);
  if (result == "null") result = "{}";

  if (verbose > 1) {
      Json::FastWriter fastWriter;
      std::string output = fastWriter.write(result);
      std::cout << "MosaikSim::get_data OUTPUT  = " << result << std::endl;
    }

  return result;
}


//---
//--- Method is not used for the current simulation
//--- If, used, need to be be rewritten together with step and get_data
//---
void
MosaikSim::set_data(void)
{
  Json::Value obj;
  Json::Value objSim;
  Json::Value objRes;
  Json::StreamWriterBuilder wbuilder;

  std::string result;
  MosaikNextSimul nsimul;

  std::string val_s;
  std::string val_d;
  std::string val_v;
  std::string val_t;

  if (verbose > 1) {
      std::cout << "MosaikSim::set_data" << std::endl;
    }

  //--- create simulator full name
  std::string full_name;
  full_name.append(mosaikSid);
  full_name.append(".");
  full_name.append(netsimProp.instance_name);

  std::string cmd = "set_data";
  obj[0] = Json::Value(cmd);

  //--- verify if there is nothing to send
  if (objNetsim->checkEmptyDataOutput() == 1)
    {
      if (verbose > 2)
        std::cout << "MosaikSim::set_data NO output data on NS3 !! " << std::endl;

      objRes.clear();

      //--- create dummy entries to send
      for (auto it = mosaikNSimul.begin(); it != mosaikNSimul.end(); it++ ){
          nsimul = (*it).second;

          if (verbose > 2)
            std::cout << "MosaikSim::set_data nsimul.target_name: " << nsimul.target_name << std::endl;

          for (uint i = 0; i < (nsimul.target_vars).size(); ++i)
            {
              if (!nsimul.target_vars[i].empty())
                objRes[nsimul.target_name][nsimul.target_vars[i]] = "null";
            }

        }

      objSim[full_name] = objRes;

    } else {  //--- if there is something in the output buffer, process them

      if (verbose > 2)
        std::cout << "MosaikSim::set_data THERE ARE output data on NS3 !! " << std::endl;

      //--- extract data
      objRes.clear();
      while (objNetsim->checkEmptyDataOutput() != 1)
        {
          objNetsim->get_data(val_s, val_d, val_v, val_t);

          if (verbose > 2)
            {
              std::cout << "MosaikSim::set_data --OUT from NS3-- "
                        << " src = "   << val_s
                        << " dst = "   << val_d
                        << " value = " << val_v
                        << " time = "  << val_t
                        << std::endl;
            }

          objRes[mosaikNSimul[val_d].target_name]["s"] = val_s;
          objRes[mosaikNSimul[val_d].target_name]["d"] = val_d;
          objRes[mosaikNSimul[val_d].target_name]["v"] = stod(val_v);
          objRes[mosaikNSimul[val_d].target_name]["t"] = stod(val_t);

        }

      objSim[full_name] = objRes;
    }

  obj[1].append(objSim);
  objRes.clear();
  obj[2] = objRes;

  //--- prepare result to send to Mosaik
  result = Json::writeString(wbuilder, obj);

  if (verbose > 1) {
      Json::FastWriter fastWriter;
      std::string output = fastWriter.write(result);
      std::cout << "MosaikSim::set_data OUTPUT  = \n" << result << std::endl;
    }

  sendRequest(result);

}


//---
//--- Method is not used for the current simulation
//--- If, used, need to be rewritten together with step and get_data
//---
std::string
MosaikSim::set_next(Json::Value args, Json::Value kwargs)
{
  if (verbose > 1)
    std::cout << "MosaikSim::set_next kwargs = \n" << kwargs << std::endl;

  std::string param;
  MosaikNextSimul nsimul;
  std::string node;

  std::vector<std::string> pextra = kwargs.getMemberNames();
  for ( auto pex_i = pextra.begin(); pex_i != pextra.end(); pex_i++ ){
      std::string param = *pex_i;

      //--- case target_name
      if (param.compare("target_name") == 0)
        {
          nsimul.target_name = (kwargs[param]).asString();

          if (verbose > 2)
            std::cout << "MosaikSim::set_next nsimul.target_name: " << nsimul.target_name << std::endl;

          //--- extract destination node name
          std::string attr;
          const char delim_pt = '.';
          const char delim_tr = '_';
          std::vector<std::string> out;
          std::vector<std::string>::iterator it;
          std::string instance;

          attr = nsimul.target_name;
          tokenize(attr, delim_pt, out);
          it = out.begin(); ++it;
          instance = (*it);

          if (verbose > 2)
            std::cout << "MosaikSim::set_next instance: " << instance << std::endl;

          attr = instance;
          out.clear();
          tokenize(attr, delim_tr, out);
          it = out.begin(); ++it;
          node = (*it);

          if (verbose > 2)
            std::cout << "MosaikSim::set_next node: " << node << std::endl;
        }

      //--- case target_vars
      if (param.compare("target_vars") == 0)
        {
          for (uint i = 0; i < (kwargs[param]).size(); i++)
            {
              nsimul.target_vars[i] = (kwargs[param][i]).asString();

              if (verbose > 2)
                std::cout << "MosaikSim::set_next Param[" << i << "]: " << nsimul.target_vars[i] << std::endl;
            }
        }

    }

  //--- insert new entry into mosaikNSimul
  mosaikNSimul[node] = nsimul;

  if (verbose > 1)
    {
      std::cout << "MosaikSim::set_next node = " << node
                << " Total entries: " << mosaikNSimul.size() << std::endl;
    }

  return "null";
}


std::string
MosaikSim::sendRequest(std::string content)
{
  std::string messages;
  Json::Value jsonMessage;
  int currentMsgId;
  std::string response;

  if (verbose > 0)
    std::cout << "MosaikSim::sendRequest" << std::endl;

  if (verbose > 1)
    std::cout << "MosaikSim::sendRequest content = \n" << content << std::endl;

  std::string result;
  int id;
  int res;

  id = nextRequestID();
  result = serialize(content,0,id);

  if (verbose > 2)
    std::cout << "MosaikSim::sendRequest result = \n" << result << std::endl;

  res = write(sock, result.c_str(), result.size());

  if (verbose > 1) {
      std::cout << "MosaikSim::sendRequest -- ASYNC REQ SENT -- Qte Bytes: " << res << std::endl;
    }

  //--- get answer from message sent
  messages = readSocket();
  jsonMessage = deserialize(messages, currentMsgId);

  if (currentMsgId == id)
    {
      if (verbose > 1)
        std::cout << "MosaikSim::sendRequest MsgId received back matched !!" << std::endl;
      response = content;
    }

  return response;
}


int
MosaikSim::nextRequestID(void)
{
  if (verbose > 1)
    std::cout << "MosaikSim::nextRequestID mosaikLastMsgId: " << mosaikLastMsgId << std::endl;

  int value = ++mosaikLastMsgId;

  if (verbose > 1)
    std::cout << "MosaikSim::nextRequestID mosaikLastMsgId, value: " << mosaikLastMsgId << " - " << value << std::endl;

  return value;
}


std::string
MosaikSim::stop(void)
{
  if (verbose > 1)
    std::cout << "MosaikSim::stop" << std::endl;

  //---
  //--- NS3 stop and destroy model
  //---
  objNetsim->~NS3Netsim();

  return "null";
}


std::string
MosaikSim::serialize(std::string result, int lastMsgOp, int lastMsgId)
{
  if (verbose > 1)
    std::cout << "MosaikSim::serialize" << std::endl;

  if (verbose > 2) {
      std::cout << "MosaikSim::serialize"
                << " lastMsgOp: " << lastMsgOp
                << " lastMsgId: " << lastMsgId
                << std::endl;
    }

  std::string output;

  output.clear();
  output.append("head");
  output.append("[");
  output.append(std::to_string(lastMsgOp));
  output.append(",");
  output.append(std::to_string(lastMsgId));
  output.append(",");
  output.append(result);
  output.append("]");

  //--- replace empty string values '""' by 'null'
  replaceAll(output, std::string("\"\""), std::string("null"));
  //--- remove end of string "\n"
  output.erase(std::remove(output.begin(), output.end(), '\n'), output.end());

  if (verbose > 1) {
      std::cout << "MosaikSim::serialize output: " << output << std::endl;
    }

  int header = htonl((uint32_t)output.size() - 4 /* header */);
  char* header_buffer = (char*) &header;
  for (int i = 0; i < 4; i++) {
      output[i] = header_buffer[i];
    }

  return output;
}


void
MosaikSim::printMsg(char* buffer, int len)
{
  std::cout << "Header:";
  for (int i = 0; i < 4 ; i++) {printf(" 0x%02X", buffer[i]);}

  std::cout << " --- Msg: ";
  for (int i = 4; i < len; i++) {
      printf("%c", buffer[i]);
    }
  std::cout << std::endl;
}


void
MosaikSim::tokenize(std::string const &str, const char delim, std::vector<std::string> &out)
{
  size_t start;
  size_t end = 0;

  while((start = str.find_first_not_of(delim, end)) != std::string::npos)
    {
      end = str.find(delim, start);
      out.push_back(str.substr(start, end - start));
    }
}


std::vector<NetSimConn>
MosaikSim::readAppConnectionsFile (std::string nodeApplicationFilename)
{
  std::vector<NetSimConn > array;
  NetSimConn s_record;
  std::vector<std::pair<std::string, std::string>> dupMap;

  if (verbose > 1)
    std::cout << "MoisaikSim::mosaikSid:readAppConnectionsFile " << nodeApplicationFilename << std::endl;

  std::fstream fin;
  fin.open(nodeApplicationFilename, ios::in);
  vector<string> row;
  string line, word;

  //--- First line ignored. It is the header
  getline(fin, line);

  while (getline(fin, line)) {
      row.clear();
      stringstream s(line);
      while (getline(s, word, ',')) {
          row.push_back(word);
        }
      if(row.size() == 10) {
          if(std::find(dupMap.begin(), dupMap.end(), std::make_pair(row[2], row[3])) != dupMap.end()) {
              if (verbose > 2)
                std::cout << "MoisaikSim::readAppConnectionsFile" <<
                          " **DUPLICATE** SRC: " << row[2] << " DST: " << row[3] << std::endl;
            } else{
              if (verbose > 2)
                std::cout << "MoisaikSim::readAppConnectionsFile" <<
                          " SRC: " << row[2] << " DST: " << row[3] << std::endl;
              s_record.src  = row[2];
              s_record.dst  = row[3];
              array.push_back(s_record);
              dupMap.push_back(std::make_pair(row[2], row[3]));
            }

        } else {
          if (verbose > 2)
            std::cout << "MoisaikSim::readAppConnectionsFile" <<
                      " Line IGNORED! Number of elements invalid " << line << std::endl;
        }
    }

  if (verbose > 2) {
      std::cout << "MoisaikSim::readAppConnectionsFile" << std::endl;
      for (auto arr_i = array.begin(); arr_i != array.end(); arr_i++ )
        {
          std::cout << "ARRAY TYPE: " << (*arr_i).type <<
                    " SRC: " << (*arr_i).src  <<
                    " DST: " << (*arr_i).dst  << std::endl;

        }
    }

  return array;
}


void
MosaikSim::replaceAll(std::string& source, const std::string& from, const std::string& to)
{
  std::string newString;
  newString.reserve(source.length());

  std::string::size_type lastPos = 0;
  std::string::size_type findPos;

  while(std::string::npos != (findPos = source.find(from, lastPos)))
    {
      newString.append(source, lastPos, findPos - lastPos);
      newString += to;
      lastPos = findPos + from.length();
    }

  newString += source.substr(lastPos);

  source.swap(newString);
}

