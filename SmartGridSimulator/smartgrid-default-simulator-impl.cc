/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * Copyright (c) 2019 University of Alberta
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
 * Date:    2019.05.12
 * Company: University of Alberta/Canada - Computing Science
 *
 * Based on code of default-simulator-impl.c from Mathieu Lacage <mathieu.lacage@sophia.inria.fr>, and
 * based on code of distributed-simulator-impl.c from George Riley <riley@ece.gatech.edu>
 *
 */

#include "simulator.h"
#include "scheduler.h"
#include "event-impl.h"

#include "ptr.h"
#include "pointer.h"
#include "assert.h"
#include "log.h"

#include <cmath>

#include "smartgrid-default-simulator-impl.h"


/**
 * \file
 * \ingroup simulator
 * ns3::DefaultSimulatorImpl implementation.
 */

namespace ns3 {

// Note:  Logging in this file is largely avoided due to the
// number of calls that are made to these functions and the possibility
// of causing recursions leading to stack overflow
NS_LOG_COMPONENT_DEFINE ("SmartgridDefaultSimulatorImpl");

NS_OBJECT_ENSURE_REGISTERED (SmartgridDefaultSimulatorImpl);

TypeId
SmartgridDefaultSimulatorImpl::GetTypeId (void)
{
  static TypeId tid = TypeId ("ns3::SmartgridDefaultSimulatorImpl")
    .SetParent<SimulatorImpl> ()
    .SetGroupName ("Core")
    .AddConstructor<SmartgridDefaultSimulatorImpl> ()
  ;
  return tid;
}

SmartgridDefaultSimulatorImpl::SmartgridDefaultSimulatorImpl ()
{
  NS_LOG_FUNCTION (this);
  m_stop = false;
  // uids are allocated from 4.
  // uid 0 is "invalid" events
  // uid 1 is "now" events
  // uid 2 is "destroy" events
  m_uid = 4;
  // before ::Run is entered, the m_currentUid will be zero
  m_currentUid = 0;
  m_currentTs = 0;
  m_currentContext = Simulator::NO_CONTEXT;
  m_unscheduledEvents = 0;
  m_eventCount = 0;
  m_eventsWithContextEmpty = true;
  m_main = SystemThread::Self();
}

SmartgridDefaultSimulatorImpl::~SmartgridDefaultSimulatorImpl ()
{
  NS_LOG_FUNCTION (this);
}

void
SmartgridDefaultSimulatorImpl::DoDispose (void)
{
  NS_LOG_FUNCTION (this);
  ProcessEventsWithContext ();

  while (!m_events->IsEmpty ())
    {
      Scheduler::Event next = m_events->RemoveNext ();
      next.impl->Unref ();
    }
  m_events = 0;
  SimulatorImpl::DoDispose ();
}
void
SmartgridDefaultSimulatorImpl::Destroy ()
{
  NS_LOG_FUNCTION (this);
  while (!m_destroyEvents.empty ()) 
    {
      Ptr<EventImpl> ev = m_destroyEvents.front ().PeekEventImpl ();
      m_destroyEvents.pop_front ();
      NS_LOG_LOGIC ("handle destroy " << ev);
      if (!ev->IsCancelled ())
        {
          ev->Invoke ();
        }
    }
}

void
SmartgridDefaultSimulatorImpl::SetScheduler (ObjectFactory schedulerFactory)
{
  NS_LOG_FUNCTION (this << schedulerFactory);
  Ptr<Scheduler> scheduler = schedulerFactory.Create<Scheduler> ();

  if (m_events != 0)
    {
      while (!m_events->IsEmpty ())
        {
          Scheduler::Event next = m_events->RemoveNext ();
          scheduler->Insert (next);
        }
    }
  m_events = scheduler;
}

// System ID for non-distributed simulation is always zero
uint32_t 
SmartgridDefaultSimulatorImpl::GetSystemId (void) const
{
  return 0;
}

void
SmartgridDefaultSimulatorImpl::ProcessOneEvent (void)
{
  Scheduler::Event next = m_events->RemoveNext ();

  NS_ASSERT (next.key.m_ts >= m_currentTs);
  m_unscheduledEvents--;
  m_eventCount++;

  NS_LOG_LOGIC ("handle " << next.key.m_ts);
  m_currentTs = next.key.m_ts;
  m_currentContext = next.key.m_context;
  m_currentUid = next.key.m_uid;
  next.impl->Invoke ();
  next.impl->Unref ();

  ProcessEventsWithContext ();
}

bool 
SmartgridDefaultSimulatorImpl::IsFinished (void) const
{
  return m_events->IsEmpty () || m_stop;
}

void
SmartgridDefaultSimulatorImpl::ProcessEventsWithContext (void)
{
  if (m_eventsWithContextEmpty)
    {
      return;
    }

  // swap queues
  EventsWithContext eventsWithContext;
  {
    CriticalSection cs (m_eventsWithContextMutex);
    m_eventsWithContext.swap(eventsWithContext);
    m_eventsWithContextEmpty = true;
  }
  while (!eventsWithContext.empty ())
    {
       EventWithContext event = eventsWithContext.front ();
       eventsWithContext.pop_front ();
       Scheduler::Event ev;
       ev.impl = event.event;
       ev.key.m_ts = m_currentTs + event.timestamp;
       ev.key.m_context = event.context;
       ev.key.m_uid = m_uid;
       m_uid++;
       m_unscheduledEvents++;
       m_events->Insert (ev);
    }
}

void
SmartgridDefaultSimulatorImpl::Run (void)
{
  NS_LOG_FUNCTION (this);
  // Set the current threadId as the main threadId
  m_main = SystemThread::Self();
  ProcessEventsWithContext ();
  m_stop = false;

  while (!m_events->IsEmpty () && !m_stop) 
    {
      ProcessOneEvent ();
    }

  // If the simulator stopped naturally by lack of events, make a
  // consistency test to check that we didn't lose any events along the way.
  NS_ASSERT (!m_events->IsEmpty () || m_unscheduledEvents == 0);
}

void 
SmartgridDefaultSimulatorImpl::Stop (void)
{
  NS_LOG_FUNCTION (this);
  m_stop = true;
}

void 
SmartgridDefaultSimulatorImpl::Stop (Time const &delay)
{
  NS_LOG_FUNCTION (this << delay.GetTimeStep ());
  Simulator::Schedule (delay, &Simulator::Stop);
}

//
// Schedule an event for a _relative_ time in the future.
//
EventId
SmartgridDefaultSimulatorImpl::Schedule (Time const &delay, EventImpl *event)
{
  NS_LOG_FUNCTION (this << delay.GetTimeStep () << event);
  NS_ASSERT_MSG (SystemThread::Equals (m_main), "Simulator::Schedule Thread-unsafe invocation!");

  NS_ASSERT_MSG (delay.IsPositive (), "SmartgridDefaultSimulatorImpl::Schedule(): Negative delay");
  Time tAbsolute = delay + TimeStep (m_currentTs);

  Scheduler::Event ev;
  ev.impl = event;
  ev.key.m_ts = (uint64_t) tAbsolute.GetTimeStep ();
  ev.key.m_context = GetContext ();
  ev.key.m_uid = m_uid;
  m_uid++;
  m_unscheduledEvents++;
  m_events->Insert (ev);
  return EventId (event, ev.key.m_ts, ev.key.m_context, ev.key.m_uid);
}

void
SmartgridDefaultSimulatorImpl::ScheduleWithContext (uint32_t context, Time const &delay, EventImpl *event)
{
  NS_LOG_FUNCTION (this << context << delay.GetTimeStep () << event);

  if (SystemThread::Equals (m_main))
    {
      Time tAbsolute = delay + TimeStep (m_currentTs);
      Scheduler::Event ev;
      ev.impl = event;
      ev.key.m_ts = (uint64_t) tAbsolute.GetTimeStep ();
      ev.key.m_context = context;
      ev.key.m_uid = m_uid;
      m_uid++;
      m_unscheduledEvents++;
      m_events->Insert (ev);
    }
  else
    {
      EventWithContext ev;
      ev.context = context;
      // Current time added in ProcessEventsWithContext()
      ev.timestamp = delay.GetTimeStep ();
      ev.event = event;
      {
        CriticalSection cs (m_eventsWithContextMutex);
        m_eventsWithContext.push_back(ev);
        m_eventsWithContextEmpty = false;
      }
    }
}

EventId
SmartgridDefaultSimulatorImpl::ScheduleNow (EventImpl *event)
{
  NS_ASSERT_MSG (SystemThread::Equals (m_main), "Simulator::ScheduleNow Thread-unsafe invocation!");

  Scheduler::Event ev;
  ev.impl = event;
  ev.key.m_ts = m_currentTs;
  ev.key.m_context = GetContext ();
  ev.key.m_uid = m_uid;
  m_uid++;
  m_unscheduledEvents++;
  m_events->Insert (ev);
  return EventId (event, ev.key.m_ts, ev.key.m_context, ev.key.m_uid);
}

EventId
SmartgridDefaultSimulatorImpl::ScheduleDestroy (EventImpl *event)
{
  NS_ASSERT_MSG (SystemThread::Equals (m_main), "Simulator::ScheduleDestroy Thread-unsafe invocation!");

  EventId id (Ptr<EventImpl> (event, false), m_currentTs, 0xffffffff, 2);
  m_destroyEvents.push_back (id);
  m_uid++;
  return id;
}

Time
SmartgridDefaultSimulatorImpl::Now (void) const
{
  // Do not add function logging here, to avoid stack overflow
  return TimeStep (m_currentTs);
}

Time 
SmartgridDefaultSimulatorImpl::GetDelayLeft (const EventId &id) const
{
  if (IsExpired (id))
    {
      return TimeStep (0);
    }
  else
    {
      return TimeStep (id.GetTs () - m_currentTs);
    }
}

void
SmartgridDefaultSimulatorImpl::Remove (const EventId &id)
{
  if (id.GetUid () == 2)
    {
      // destroy events.
      for (DestroyEvents::iterator i = m_destroyEvents.begin (); i != m_destroyEvents.end (); i++)
        {
          if (*i == id)
            {
              m_destroyEvents.erase (i);
              break;
            }
        }
      return;
    }
  if (IsExpired (id))
    {
      return;
    }
  Scheduler::Event event;
  event.impl = id.PeekEventImpl ();
  event.key.m_ts = id.GetTs ();
  event.key.m_context = id.GetContext ();
  event.key.m_uid = id.GetUid ();
  m_events->Remove (event);
  event.impl->Cancel ();
  // whenever we remove an event from the event list, we have to unref it.
  event.impl->Unref ();

  m_unscheduledEvents--;
}

void
SmartgridDefaultSimulatorImpl::Cancel (const EventId &id)
{
  if (!IsExpired (id))
    {
      id.PeekEventImpl ()->Cancel ();
    }
}

bool
SmartgridDefaultSimulatorImpl::IsExpired (const EventId &id) const
{
  if (id.GetUid () == 2)
    {
      if (id.PeekEventImpl () == 0 ||
          id.PeekEventImpl ()->IsCancelled ())
        {
          return true;
        }
      // destroy events.
      for (DestroyEvents::const_iterator i = m_destroyEvents.begin (); i != m_destroyEvents.end (); i++)
        {
          if (*i == id)
            {
              return false;
            }
        }
      return true;
    }
  if (id.PeekEventImpl () == 0 ||
      id.GetTs () < m_currentTs ||
      (id.GetTs () == m_currentTs &&
       id.GetUid () <= m_currentUid) ||
      id.PeekEventImpl ()->IsCancelled ()) 
    {
      return true;
    }
  else
    {
      return false;
    }
}

Time 
SmartgridDefaultSimulatorImpl::GetMaximumSimulationTime (void) const
{
  return TimeStep (0x7fffffffffffffffLL);
}

uint32_t
SmartgridDefaultSimulatorImpl::GetContext (void) const
{
  return m_currentContext;
}

uint64_t
SmartgridDefaultSimulatorImpl::GetEventCount (void) const
{
  return m_eventCount;
}

Time
SmartgridDefaultSimulatorImpl::Next (void) const
{
  return TimeStep (NextTs ());
}

uint64_t
SmartgridDefaultSimulatorImpl::NextTs (void) const
{
  // If local MPI task is has no more events or stop was called
  // next event time is infinity.
  if (IsLocalFinished ())
    {
      return GetMaximumSimulationTime ().GetTimeStep ();
    }
  else
    {
      Scheduler::Event ev = m_events->PeekNext ();
      return ev.key.m_ts;
    }
}

bool
SmartgridDefaultSimulatorImpl::IsLocalFinished (void) const
{
  return m_events->IsEmpty () || m_stop;
}

Scheduler::Event
SmartgridDefaultSimulatorImpl::PeekNextEvent(void) const
{
	return m_events->PeekNext ();
}

Scheduler::Event
SmartgridDefaultSimulatorImpl::RemoveNextEvent(void) const
{
	return m_events->RemoveNext ();
}

void
SmartgridDefaultSimulatorImpl::RunUntil (const Time &checkTime)
{
	  NS_LOG_FUNCTION (this);
	  // Set the current threadId as the main threadId
	  m_main = SystemThread::Self();
	  ProcessEventsWithContext ();
	  m_stop = false;

	  while (!m_events->IsEmpty () && !m_stop && NextTs () < (unsigned long)checkTime.GetInteger())
		{
		  ProcessOneEvent ();
		}

	  // If the simulator stopped naturally by lack of events, make a
	  // consistency test to check that we didn't lose any events along the way.
	  NS_ASSERT (!m_events->IsEmpty () || m_unscheduledEvents == 0);
}

} // namespace ns3
