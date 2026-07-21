export * as PublicEventManifest from "./public-event-manifest"

import { Event } from "@exos-agent/schema/event"
import { EventManifest } from "@exos-agent/schema/event-manifest"

export const Definitions = EventManifest.ServerDefinitions
export const Latest = Event.latest(Definitions)
