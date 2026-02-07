#!/usr/bin/env python3
"""Query Ableton Live session state via AbletonOSC.

Returns JSON describing the current session: tempo, tracks, clips, devices.
"""

import json
import sys
import time
import threading
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class AbletonQuery:
    def __init__(self, host="127.0.0.1", send_port=11000, recv_port=11001):
        self.client = SimpleUDPClient(host, send_port)
        self.responses = {}

        self.dispatcher = Dispatcher()
        self.dispatcher.set_default_handler(self._handle_response)
        self.server = BlockingOSCUDPServer((host, recv_port), self.dispatcher)

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def _handle_response(self, address, *args):
        self.responses[address] = args

    def query(self, address, *args, timeout=0.5):
        self.responses.pop(address, None)
        self.client.send_message(address, list(args))
        time.sleep(timeout)
        return self.responses.get(address)

    def shutdown(self):
        self.server.shutdown()

    def get_session_info(self):
        return {
            "tempo": self.query("/live/song/get/tempo"),
            "num_tracks": self.query("/live/song/get/num_tracks"),
            "num_scenes": self.query("/live/song/get/num_scenes"),
            "signature_numerator": self.query("/live/song/get/signature_numerator"),
            "signature_denominator": self.query("/live/song/get/signature_denominator"),
        }

    def get_track_info(self, track_idx):
        return {
            "index": track_idx,
            "name": self.query("/live/track/get/name", track_idx),
            "volume": self.query("/live/track/get/volume", track_idx),
            "panning": self.query("/live/track/get/panning", track_idx),
            "mute": self.query("/live/track/get/mute", track_idx),
            "solo": self.query("/live/track/get/solo", track_idx),
            "arm": self.query("/live/track/get/arm", track_idx),
        }

    def get_all_tracks(self):
        num = self.query("/live/song/get/num_tracks")
        if not num:
            return []
        tracks = []
        for i in range(int(num[0])):
            tracks.append(self.get_track_info(i))
        return tracks

    def get_clip_slots(self, track_idx):
        return self.query("/live/track/get/clips/name", track_idx)

    def get_devices(self, track_idx):
        return self.query("/live/track/get/devices/name", track_idx)

    def get_device_params(self, track_idx, device_idx=0):
        """Get parameter names and values for a device."""
        names = self.query("/live/device/get/parameters/name", track_idx, device_idx)
        values = self.query("/live/device/get/parameters/value", track_idx, device_idx)
        if names and values:
            # First two elements are track_idx and device_idx
            param_names = [str(n) for n in names[2:]]
            param_values = [v for v in values[2:]]
            return [
                {"index": i, "name": param_names[i], "value": round(float(param_values[i]), 4) if i < len(param_values) else None}
                for i in range(len(param_names))
            ]
        return names


def main():
    q = AbletonQuery()

    subcmd = sys.argv[1] if len(sys.argv) > 1 else "session"

    if subcmd == "session":
        result = q.get_session_info()
    elif subcmd == "tracks":
        result = q.get_all_tracks()
    elif subcmd == "track":
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        result = q.get_track_info(idx)
    elif subcmd == "clips":
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        result = q.get_clip_slots(idx)
    elif subcmd == "devices":
        idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        result = q.get_devices(idx)
    else:
        print(f"Unknown query: {subcmd}", file=sys.stderr)
        print("Available: session, tracks, track <n>, clips <n>, devices <n>", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2, default=str))
    q.shutdown()


if __name__ == "__main__":
    main()
