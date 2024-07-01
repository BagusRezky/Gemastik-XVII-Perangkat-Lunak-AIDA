# AIDA : Sistem Manajemen Reklame Cerdas Luar Ruang berbasis Kecerdasan Buatan
AIDA merupakan aplikasi manajemen billboard cerdas yang mampu menghitung objek yang melewati billboard secara otomatis. Aplikasi ini dibuat untuk memenuhi kebutuhan dalam mengelola reklame luar ruang yang lebih efisien dan efektif. AIDA menggunakan teknologi kecerdasan buatan YOLO untuk mendeteksi objek yang melewati billboard dan menghitung jumlahnya. AIDA juga dilengkapi dengan fitur analisis data yang memungkinkan pengguna untuk melihat data jumlah objek yang melewati billboard dalam bentuk grafik. 

## Anggota Tim
1. Andi Dwi Prasetyo
2. Bagus Rezky Adhyaksa
3. Anisa Rahmasari
4. Dosen Pembimbing : Muhammad Afif Hendrawan,S.Kom., M.T.

## Cara Penggunaan
1. Clone repository

   `$ git clone https://github.com/BagusRezky/Gemastik-XVII-Perangkat-Lunak-AIDA.git`

2. Download Video yang telah disediakan di Download.txt
3. Install required dependencied
   
   `$ pip install -r requirements.txt`

4. Download dan konfigurasi Mosquitto MQTT Broker
   
   A. Download Mosquitto MQTT Broker di https://mosquitto.org/download/

   B. Konfigurasi Mosquitto MQTT Broker
      - Buka file mosquitto.conf yang terletak di C:\Program Files\mosquitto
      - Tambahkan baris berikut pada file mosquitto.conf
        ```
        listener 1883
        protocol websockets
        listener 9001
        log_type all
        allow_anonymous true
        log_type debug
        ```
      - Jalankan Mosquitto MQTT Broker di cmd
        
        `$ mosquitto -c mosquitto.conf -v`

5. Download dan konfigurasi FFmpeg

   A. Download FFmpeg di https://ffmpeg.org/download.html

   B. Konfigurasi FFmpeg
      - Extract file FFmpeg yang telah di download
      - Tambahkan folder bin ke environtment path system
      - Cek apakah FFmpeg sudah terinstall dengan mengetik perintah berikut di cmd
        ```
        ffmpeg -version
        ```
6. Konfigurasi Server NGINX-RTMP

   A. Ganti path hls_path dan alias nginx.conf sesuai folder anda

   B. Jalankan server NGINX-RTMP di cmd

      ```
      start nginx -> untuk start server
      nginx -s stop -> untuk stop server
      ```
7.  Jalankan Main.py
   
    `$ python main.py --video 'path_to_video' --model 'path_to_model' --label 'path_to_label' --rtmp_url 'path_to_rtmp_url'`
    
    ### Example
    `$ python main.py --video '..\veh2.mp4' --model 'yolov3-tinyu.pt' --label '..\coco.txt' --rtmp_url 'rtmp://localhost/live/test'`
    * Replace `'path_to_video'` with the path to the input video file.
    * Replace `'path_to_model'` with the path to the YOLOv model (`yolov3-tinyu.pt` in the original form).
    * Replace `'path_to_label'` with the path to the file containing the labels (e.g., `coco.txt`)
    * Replace `'path_to_rtmp_url'` with the RTMP URL for the server. The default URL is `'rtmp://localhost/live/test'`.
  
8.  Jalankan Web
   
      A. Jalankan Web
      
      `$ npm run dev`

