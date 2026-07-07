from flask import Flask, request, jsonify
import csv
import json
import os

app = Flask(__name__, static_folder='.', static_url_path='')

CSV_DOSYASI = 'harcamalar.csv'
JSON_DOSYASI = 'ayarlar.json' 

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/yukle', methods=['GET'])
def yukle():
    harcamalar = []
    # CSV dosyasından harcamaları oku
    if os.path.exists(CSV_DOSYASI):
        with open(CSV_DOSYASI, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                row['id'] = float(row['id']) if row['id'] else 0
                row['tutar'] = float(row['tutar']) if row['tutar'] else 0.0
                row['yemekKartiIle'] = row['yemekKartiIle'] == 'True'
                # Eski kayıtlarda ödeme yöntemi yoksa varsayılan olarak Kredi Kartı ata
                row['odemeYontemi'] = row.get('odemeYontemi') or 'Kredi Kartı'
                
                for k, v in row.items():
                    if v == 'null' or v == '':
                        row[k] = None
                harcamalar.append(row)
    
    # Bütçe ve kategorileri JSON'dan oku
    diger_veriler = {'butceler': {}, 'ozelKategoriler': [], 'abonelikler': []}
    if os.path.exists(JSON_DOSYASI):
        with open(JSON_DOSYASI, mode='r', encoding='utf-8') as f:
            diger_veriler = json.load(f)
            
    return jsonify({'harcamalar': harcamalar, 'diger': diger_veriler})

@app.route('/kaydet', methods=['POST'])
def kaydet():
    veri = request.json
    harcamalar = veri.get('harcamalar', [])
    diger = veri.get('diger', {})
    
    # Harcamaları CSV'ye yaz (odemeYontemi eklendi)
    if harcamalar:
        with open(CSV_DOSYASI, mode='w', encoding='utf-8', newline='') as f:
            fieldnames = ['id', 'groupId', 'abonelikId', 'tarih', 'ay', 'aciklama', 'kategori', 'kisi', 'yemekKartiIle', 'odemeYontemi', 'tutar', 'taksitBilgisi']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(harcamalar)
    else:
        with open(CSV_DOSYASI, mode='w', encoding='utf-8', newline='') as f:
            pass 
            
    with open(JSON_DOSYASI, mode='w', encoding='utf-8') as f:
        json.dump(diger, f, ensure_ascii=False, indent=4)
        
    return jsonify({"durum": "basarili"})

if __name__ == '__main__':
    print("Tarayıcıda şu adrese gidin: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
