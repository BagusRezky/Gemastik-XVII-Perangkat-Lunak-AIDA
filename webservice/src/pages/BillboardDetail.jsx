import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import mqtt from "mqtt";

function BillboardDetail() {
  const { id } = useParams();
  const [interactions, setInteractions] = useState({ down: 0, up: 0 });

  useEffect(() => {
    const client = mqtt.connect("mqtt://localhost:1883");

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

    return () => {
      client.end();
    };
  }, []);

  useEffect(() => {
    const player = videojs(document.getElementById("rtsp-video"), {
      autoplay: true,
      controls: true,
      sources: [
        {
          src: "rtsp://localhost:8554/mystream",
          type: "application/x-rtsp",
        },
      ],
    });

    player.on("error", (e) => {
      console.log("Error with video.js player:", e);
    });

    return () => {
      if (player) {
        player.dispose();
      }
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
          id="rtsp-video"
          className="video-js vjs-default-skin"
          width="850"
          height="480"
          controls
        ></video>
        <div className="bg-gray-100 p-9 rounded">
          <p className="text-md mb-2">{`Hari/Tanggal: ${billboard.date}`}</p>
          <p className="text-md mb-2">{`Lokasi: ${billboard.location}`}</p>
          <p className="text-md mb-2">{`Waktu: ${billboard.time}`}</p>
          <div className="mt-10 text-center">
            <p className="text-2xl font-bold">Jumlah Interaksi</p>
            <p className="text-5xl font-bold">{`Down: ${interactions.down}`}</p>
            <p className="text-5xl font-bold">{`Up: ${interactions.up}`}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BillboardDetail;
