import math

class Tracker:
    def __init__(self):
        # Menyimpan posisi pusat objek
        self.center_points = {}
        # Menyimpan jumlah ID
        # Setiap kali objek baru terdeteksi, ID bertambah satu
        self.id_count = 0

    def update(self, objects_rect):
        # Kotak objek dan ID
        objects_bbs_ids = []

        # Mendapatkan titik pusat objek baru
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2

            # Mencari tahu apakah objek tersebut sudah terdeteksi
            same_object_detected = False
            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])

                if dist < 35:  # Jika jarak pusatnya kurang dari threshold
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                    break

            # Objek baru terdeteksi, berikan ID ke objek tersebut
            if not same_object_detected:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1

        # Membersihkan dictionary dengan menghapus ID yang tidak digunakan lagi
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        # Memperbarui dictionary dengan ID yang tidak digunakan dihapus
        self.center_points = new_center_points.copy()

        return objects_bbs_ids
