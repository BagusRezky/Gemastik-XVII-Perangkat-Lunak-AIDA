import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import mqtt from "mqtt";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import Hls from "hls.js";

function BillboardDetail() {
  const { id } = useParams();
  const videoRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [interactions, setInteractions] = useState({
    going_down: 0,
    going_up: 0,
  });

  useEffect(() => {
    // Membuat permintaan Axios untuk memastikan CORS
    const fetchHlsManifest = async () => {
      try {
        const response = await axios.get("http://localhost:8080/hls/test.m3u8");
        if (response.status === 200) {
          setVideoUrl("http://localhost:8080/hls/test.m3u8");
          setIsReady(true);
        }
      } catch (error) {
        console.error("Error fetching HLS manifest:", error);
      }
    };

    fetchHlsManifest();
  }, []);

  useEffect(() => {
    if (isReady && videoRef.current) {
      const videoElement = videoRef.current;
      let player;

      if (Hls.isSupported()) {
        const hls = new Hls();
        hls.loadSource(videoUrl);
        hls.attachMedia(videoElement);
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          videoElement.muted = true;
          videoElement.play().catch((error) => {
            console.error("Error attempting to play:", error);
          });
        });
      } else if (videoElement.canPlayType("application/vnd.apple.mpegurl")) {
        videoElement.src = videoUrl;
        videoElement.addEventListener("loadedmetadata", () => {
          videoElement.muted = true;
          videoElement.play().catch((error) => {
            console.error("Error attempting to play:", error);
          });
        });
      }

      player = videojs(videoElement, {
        autoplay: false,
        controls: true,
        techOrder: ["html5"],
      });

      player.on("ready", () => {
        console.log("Video.js player is ready");
        videoElement.muted = true;
        videoElement.play().catch((error) => {
          console.error("Error attempting to play:", error);
        });
      });

      player.on("error", (e) => {
        console.error("Error with video.js player:", e);
      });

      return () => {
        if (player) {
          player.dispose();
        }
      };
    }
  }, [isReady, videoUrl]);


  useEffect(() => {
    const client = mqtt.connect("ws://localhost:9001/mqtt");

    client.on("connect", () => {
      console.log("Connected to MQTT broker");
      client.subscribe("vehicle/interactions", (err) => {
        if (!err) {
          console.log("Subscribed to vehicle/interactions");
        }
      });
    });

    client.on("message", (topic, message) => {
      if (topic === "vehicle/interactions") {
        const data = JSON.parse(message.toString());
        console.log("Received MQTT message:", data);
        setInteractions(data);
      }
    });

    client.on("error", (err) => {
      console.error("MQTT Connection Error: ", err);
    });

    return () => {
      client.end();
    };
  }, []);


  const billboard = {
    id,
    size: "4x8",
    address: "Jl. Raya Bogor, No. 5, Jakarta",
    date: "Kamis, 7 Februari 2024",
    time: "13.40",
    location: "Jl. Soekarno Hatta",
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Billboard Detail</h2>
      <div className="flex flex-wrap justify-around items-center mt-2">
        <video
          ref={videoRef}
          id="rtmp-video"
          className="video-js vjs-default-skin"
          width="850"
          height="480"
          controls
        ></video>
        {!isReady && <p>Loading video...</p>}
        {isReady && (
          <div className="bg-gray-100 p-9 rounded">
            <p className="text-md mb-2">{`Hari/Tanggal: ${billboard.date}`}</p>
            <p className="text-md mb-2">{`Lokasi: ${billboard.location}`}</p>
            <p className="text-md mb-2">{`Waktu: ${billboard.time}`}</p>
            <div className="mt-10 text-center">
              <p className="text-2xl font-bold">Jumlah Interaksi</p>
              <p className="text-5xl font-bold">{`Down: ${interactions.going_down}`}</p>
              <p className="text-5xl font-bold">{`Up: ${interactions.going_up}`}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BillboardDetail;

