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


#ifndef MOSAIKSIM_H_
#define MOSAIKSIM_H_

//--- C Includes
#include <assert.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <jsoncpp/json/json.h>

//--- C++ Includes
#include <iostream>
#include <algorithm>
#include <string>
#include <fstream>
#include <sstream>
#include <array>
#include <cstdint>


//--- NS3
#include "NS3Netsim.h"


#define BUFFER_SIZE 4194304	//--- Maximum Mosaik message size: Buffer size 1024 * 1024 * 4 bytes
#define MAXRECV     30000   //--- Socket receiving maximum size

/**
 * \brief Host IP and port structure
 */
struct AddrPort {
    std::string host;
    uint16_t port;
};


/**
 * \brief Mosaik commands enumeration
 */
enum MosaikCommand {
    cmdInit,
    cmdCreate,
    cmdSetup_done,
    cmdStep,
    cmdGet_data,
    cmdStop,
    cmdGet_progress,
    cmdGet_related_entities,
    cmdSet_data,
    cmdSet_next
};


/**
 * \brief Mosaik operation results
 */
enum MosaikMsgProcess {
    SUCCESS = 1,
    FAILURE = 2
};


#define MAX_MOSAIK_ITEMS 24	     //--- Maximum number of parameters
#define MAX_SIMULATOR_LINKS 2048 //--- Maximum number of attributes


/**
 * \brief Mosaik model structure
 */
struct MosaikModel {
    std::string access;
    std::string params[MAX_MOSAIK_ITEMS];
    std::string attrs[MAX_SIMULATOR_LINKS];
};


/**
 * \brief Mosaik meta model structure
 */
struct MosaikMeta {
    std::string api_version;
    std::string model;
    MosaikModel props[MAX_MOSAIK_ITEMS];
    std::string extra_methods[MAX_MOSAIK_ITEMS];
};


/**
 * \brief Mosaik downstream connected simulators structure
 */

struct MosaikNextSimul {
    std::string source_name;
    std::string target_name;
    std::array<std::string,MAX_MOSAIK_ITEMS> target_vars;
};


/**
 * \brief Network simulator properties
 */
struct NetSimProp {
    std::string model_name;
    std::string eid_prefix;
    std::string instance_name;
    double start_time;
    double stop_time;
    double random_seed;
    double seconds_per_mosaik_timestep;
    double step_size;
    std::string appcon_file;
    std::string adjmat_file;
    std::string coords_file;
    std::string linkRate;
    std::string linkDelay;
    std::string linkErrorRate;
    int verbose;
    std::string tcpOrUdp;
};


/**
 * \brief Network simulator source-destination connection structure
 */
struct NetSimConn {
    std::string src;
    std::string dst;
    std::string type;
};



class MosaikSim {
 public:

  /**
   * Constructor of the class Simulator
   *
   * \param varargin String argument; server ip and port; format: 'ip:port'.
   *
   * \returns Simulator object
   */
  MosaikSim(std::string varargin, NS3Netsim *obj);

  /**
   * Destructor of the class MosaikSim
   *
   * \returns Simulator object
   */
  virtual ~MosaikSim();


 private:

  //---
  //--- MosaikSim variables
  //---
  int verbose;
  std::string host;
  uint16_t port;
  int sock;
  char buffer[BUFFER_SIZE];
  struct sockaddr_in serv_addr;
  bool stopServer;
  NS3Netsim *objNetsim;

  //---
  //--- Mosaik variables
  //---
  MosaikModel mosaikModel;	///< Mosaik model structure variable
  MosaikMeta  mosaikMeta;     ///< Mosaik meta model structure variable

  std::string mosaikSid;		///< Simulator ID
  std::string mosaikSimModel; ///< Instance name
  int mosaikNum;				///< Number of instances of the simulator to create
  int mosaikLastMsgId;		///< Last message ID
  uint64_t mosaikTime;		///< Mosaik meta model structure variable

  enum MosaikMsgProcess mosaikLastMsgOp; ///< Result of the last operation

  ///< Map to associate the strings with the enum values
  std::map<std::string, MosaikCommand> mapMosaikCommands;

  ///< Simulators connected downstream
  std::map<std::string, MosaikNextSimul> mosaikNSimul;

  ///< Map to store extracted data from NS3
  std::map<std::pair<std::string, std::string>, std::pair<std::string, std::string>> mapGetData;


  //---
  //--- NetSim variables
  //---
  NetSimProp netsimProp;                           ///< Network simulator properties
  std::map<std::string, std::string> netsimParams; ///< Network simulator parameters
  std::map<std::string, std::pair<std::string, std::string>> netsimEntities;         ///< Network simulator entities
  std::vector<NetSimConn> vecNetSimConn;           ///< Network simulator connections

  //---
  //--- Transporter model variables
  //---
  MosaikModel TransporterModel = {.access = "True",
      .params = {"src", "dst"},
      .attrs = {"v", "t"}
  };

  MosaikMeta TransporterMeta = {.api_version = {"2.4"},
      .model = "Transporter",
      .props = {TransporterModel}
  };



  //---
  //--- Private Methods
  //---

  /**
   * \brief Open TCP connection with Mosaik server
   *
   * \param none
   * \returns none
   *
   */
  void openSocket(void);


  /**
   * \brief Starts main loop.
   *
   * \param none
   * \returns none
   *
   */
  void startMainLoop(void);


  /**
   * \brief Activates server stop toggle.
   *
   * \param none
   * \returns none
   *
   */
  void stopMainLoop(void);


  /**
   * \brief Waits for message, deserializes it, sends request to Mosaik command,
   * receives answer from Mosaik command, serializes it, sends it socket.Activates server stop toggle.
   *
   * \param none
   * \returns none
   *
   */
  void mainLoop(void);


  /**
   * \brief Waits for Messages in the Socket and return these, usually this should be only one message
   *
   * \param none
   * \returns msgs message read
   *
   */
  std::string readSocket(void);


  /**
   * \brief Splits the received buffer into the different messages,
   * saves incomplete messages to for next loopWaits for Messages in
   * the Socket and return these, usually this should be only one message
   *
   * NOT COMPLETELY IMPLEMENTED
   *
   * \param bufsize buffer size
   * \returns msgs message read
   *
   */
  std::string	splitRequest(int bufsize);


  /**
   * \brief Converts response from MosaikSim data types to JSON.
   *
   *
   * \param result: String argument; message content
   * \param lastMsgOp: execution result of the last operation
   * \param last MsgId: last message id.
   *
   * \returns message: message to send
   *
   */
  std::string serialize(std::string result, int lastMsgOp, int lastMsgId);


  /**
   * \brief Extract message Id, type and content
   *
   *
   * \param result: String argument; message content.
   * \param last MsgId: last message id.
   *
   * \returns message: content received
   *
   */
  Json::Value deserialize(std::string payload, int& currentMsgId);

  /*
   * Middleware methods
   */
  std::string simSocketReceivedRequest(Json::Value messages);
  void initMosaikCommands(void);
  std::string sendRequest(std::string content);
  int nextRequestID(void);
  std::string dscrListForEntities(std::string eid);

  /*
   * Mosaik commands and replays
   */
  std::string init(Json::Value args, Json::Value kwargs);
  std::string meta(void);
  std::string create(Json::Value args, Json::Value kwargs);
  std::string setup_done(void);
  std::string step(Json::Value args, Json::Value kwargs);
  std::string get_data(Json::Value args, Json::Value kwargs);
  std::string set_next(Json::Value args, Json::Value kwargs);
  std::string stop(void);
  void set_data(void);


  /*
   * Utility methods
   */
  AddrPort parseAddress(std::string param);
  void printMsg(char* buffer, int len);
  std::vector<NetSimConn> readAppConnectionsFile (std::string nodeApplicationFilename);
  void tokenize(std::string const &str, const char delim, std::vector<std::string> &out);
  bool is_number(const std::string& s);
  void replaceAll(std::string& source, const std::string& from, const std::string& to);

};

#endif /* MOSAIKSIM_H_ */
