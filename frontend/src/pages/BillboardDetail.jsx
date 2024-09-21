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
  const playerRef = useRef(null);
  const [isReady, setIsReady] = useState(false);
  const [videoUrl, setVideoUrl] = useState("");
  const [interactions, setInteractions] = useState({
    going_down: 0,
    going_up: 0,
  });

  // State untuk tanggal dan waktu
  const [currentTime, setCurrentTime] = useState({
    date: "",
    time: "",
  });

  // Fungsi untuk format tanggal dan waktu
  const formatDateTime = () => {
    const now = new Date();

    // Format hari (dalam bahasa Indonesia)
    const days = [
      "Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu",
    ];
    const dayName = days[now.getDay()];

    // Format tanggal dalam format DD MMMM YYYY
    const months = [
      "Januari", "Februari", "Maret", "April", "Mei", "Juni",
      "Juli", "Agustus", "September", "Oktober", "November", "Desember",
    ];
    const day = now.getDate();
    const month = months[now.getMonth()];
    const year = now.getFullYear();

    const formattedDate = `${dayName}, ${day} ${month} ${year}`;

    // Format waktu dalam format HH.MM
    const hours = now.getHours().toString().padStart(2, "0");
    const minutes = now.getMinutes().toString().padStart(2, "0");
    const formattedTime = `${hours}.${minutes}`;

    return { formattedDate, formattedTime };
  };

  // Mengambil tanggal dan waktu setiap detik
  useEffect(() => {
    const updateDateTime = () => {
      const { formattedDate, formattedTime } = formatDateTime();
      setCurrentTime({
        date: formattedDate,
        time: formattedTime,
      });
    };

    updateDateTime(); // Memanggil pertama kali
    const intervalId = setInterval(updateDateTime, 1000); // Perbarui setiap detik

    return () => clearInterval(intervalId); // Bersihkan interval saat komponen unmount
  }, []);

  useEffect(() => {
    if (!videoUrl) {
      const fetchHlsManifest = async () => {
        try {
          const response = await axios.get("http://103.245.38.40/hls/test.m3u8");
          if (response.status === 200) {
            setVideoUrl("http://103.245.38.40/hls/test.m3u8");
            setIsReady(true);
          }
        } catch (error) {
          console.error("Error fetching HLS manifest:", error);
        }
      };
      fetchHlsManifest();
    }
  }, [videoUrl]);

  useEffect(() => {
    if (isReady && videoRef.current) {
      const videoElement = videoRef.current;

      if (!playerRef.current) {
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

        playerRef.current = videojs(videoElement, {
          autoplay: true,
          muted: true,
          controls: false,
          techOrder: ["html5"],
        });

        playerRef.current.on("ready", () => {
          console.log("Video.js player is ready");
          videoElement.muted = true;
          videoElement.play().catch((error) => {
            console.error("Error attempting to play:", error);
          });
        });

        playerRef.current.on("error", (e) => {
          console.error("Error with video.js player:", e);
        });
      }

      return () => {
        if (playerRef.current) {
          // Jangan dispose player saat komponen di-unmount
        }
      };
    }
  }, [isReady, videoUrl]);

  useEffect(() => {
    const client = mqtt.connect("ws://103.245.38.40:9001/mqtt");

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
          width="640"
          height="480"
          autoPlay
          muted
        ></video>
        {!isReady && <p>Loading video...</p>}
        {isReady && (
          <div className="bg-gray-100 p-9 rounded">
            {/* Menampilkan waktu dinamis */}
            <p className="text-md mb-2">{`Hari/Tanggal: ${currentTime.date}`}</p>
            <p className="text-md mb-2">{`Waktu: ${currentTime.time}`}</p>
            <p className="text-md mb-2">{`Lokasi: ${billboard.location}`}</p>
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
