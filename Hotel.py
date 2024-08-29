import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, time, timedelta
import base64
import io
from fpdf import FPDF

#Kelas PDF untuk membuat bukti pemesanan
class PDF(FPDF):
    def header(self):
        self.set_fill_color(230, 230, 230)  # Background abu-abu terang untuk header
        self.rect(0, 0, 210, 20, 'F')  # Isi background header
        
        self.image('LogoAI.png', 10, 8, 33)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Xaravy Hotel', 0, 1, 'C', fill=False)
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'Reservation Confirmation', 0, 1, 'C', fill=False)
        self.ln(5)

    def footer(self):
        self.set_y(-30)
        self.set_fill_color(230, 230, 230)  # Background abu-abu terang untuk footer
        self.rect(0, 267, 210, 30, 'F')  # Isi background footer

        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, 'Xaravy Hotel', 0, 1, 'C', fill=False)
        self.cell(0, 5, 'Xaravy Hotel Kramat 98, Jakarta, Indonesia', 0, 1, 'C', fill=False)
        self.cell(0, 5, 'Phone: (123) 456-7890', 0, 1, 'C', fill=False)
        self.cell(0, 5, 'Email: info@xaravahotel.com', 0, 1, 'C', fill=False)

# Kelas untuk mengelola reservasi hotel
class HotelReservation:
    def __init__(self):
        if "rooms" not in st.session_state:
            st.session_state["rooms"] = {
                "Single": [],
                "Standard": [],
                "Deluxe": [],
                "Suite": [],
                "Superior": []
            }
        if "reservations" not in st.session_state:
            st.session_state["reservations"] = []
        if "checkout_history" not in st.session_state:
            st.session_state["checkout_history"] = []

    # Mendapatkan harga kamar
    def get_room_prices(self):
        return {
            "Single": 100000,
            "Standard": 150000,
            "Deluxe": 200000,
            "Suite": 300000,
            "Superior": 500000
        }

    # Menampilkan kamar yang tersedia
    def display_available_rooms(self):
        available_rooms = {
            room_type: len([room for room in room_list if not room['reserved']])
            for room_type, room_list in st.session_state["rooms"].items()
        }
        room_prices = self.get_room_prices()
        return available_rooms, room_prices, st.session_state["rooms"]

    # Pesan kamar
    def dequeue_reservation(self, room_type, guest_name, guest_phone, check_in_datetime, check_out_datetime, payment_method):
        room_prices = self.get_room_prices()
        
        #Dequeue Pengambilan Nomor Kamar jenis
        if room_type in st.session_state["rooms"]:
            for room in st.session_state["rooms"][room_type]:
                if not room['reserved']:
                    room['reserved'] = True
                    total_days = (check_out_datetime - check_in_datetime).days
                    total_price = room_prices[room_type] * total_days
                    reservation = {
                        "Nomor Kamar": room['number'],
                        "Tipe Kamar": room_type,
                        "Nama Pelanggan": guest_name,
                        "Nomor Telepon": guest_phone,
                        "Check In": check_in_datetime,
                        "Check Out": check_out_datetime,
                        "Konfirmasi Check-In": False,
                        "Total Harga": total_price,
                        "Check In Telah Dikonfirmasi": None,
                        "Metode Pembayaran": payment_method
                    }
                    st.session_state["reservations"].append(reservation)
                    return reservation  # Mengembalikan ke reservasi
        return None  # Kembali kosong jika kamar tidak tersedia

    # Membuat bukti reservasi dalam bentuk PDF
    def generate_reservation_pdf(self, reservation):
        pdf = PDF()
        pdf.add_page()

        # Penambahan Judul
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 20, txt="Bukti Pemesanan Kamar Hotel", ln=True, align="C")
        
        # Penambahan detail reservasi
        pdf.set_font("Arial", size=10)
        pdf.ln(10)
        
        pdf.set_fill_color(240, 240, 240)  # Latar belakang abu-abu terang untuk judul tabel
        pdf.cell(50, 10, "Detail Reservasi", ln=1, align="L", fill=True)
        
        pdf.cell(50, 10, "Nomor Kamar:", border=1, fill=True)
        pdf.cell(100, 10, reservation['Nomor Kamar'], border=1, ln=1, fill=True)
        
        pdf.cell(50, 10, "Tipe Kamar:", border=1, fill=True)
        pdf.cell(100, 10, reservation['Tipe Kamar'], border=1, ln=1, fill=True)
        
        pdf.cell(50, 10, "Nama Pelanggan:", border=1, fill=True)
        pdf.cell(100, 10, reservation['Nama Pelanggan'], border=1, ln=1, fill=True)
        
        pdf.cell(50, 10, "Nomor Telepon:", border=1, fill=True)
        pdf.cell(100, 10, reservation['Nomor Telepon'], border=1, ln=1, fill=True)
        
        pdf.cell(50, 10, "Check In:", border=1, fill=True)
        pdf.cell(100, 10, reservation['Check In'].strftime("%Y-%m-%d %H:%M"), border=1, ln=1, fill=True)
        
        pdf.cell(50, 10, "Check Out:", border=1, fill=True)
        pdf.cell(100, 10, reservation['Check Out'].strftime("%Y-%m-%d %H:%M"), border=1, ln=1, fill=True)
        
        pdf.cell(50, 10, "Total Harga:", border=1, fill=True)
        pdf.cell(100, 10, f"Rp {reservation['Total Harga']:,}", border=1, ln=1, fill=True)
        
        pdf.cell(50, 10, "Metode Pembayaran:", border=1, fill=True)
        pdf.cell(100, 10, reservation['Metode Pembayaran'], border=1, ln=1, fill=True)
        
        pdf_output = io.BytesIO()
        pdf_output.write(pdf.output(dest='S').encode('latin1'))
        return pdf_output

    # Enqueue kamar nomor dan jenis kamar
    def enqueue_add_room(self, room_type, room_number):

        # Penggunaan logika untuk nomor kamar
        if not room_number.isdigit():
            return "Nomor kamar harus berupa angka."

        if room_type in st.session_state["rooms"]:
            for room in st.session_state["rooms"][room_type]:
                if room['number'] == room_number:
                    return f"Nomor kamar {room_number} sudah ada di tipe kamar {room_type}."
            room = {
                "number": room_number,
                "reserved": False
            }
            st.session_state["rooms"][room_type].append(room)
            return f"Berhasil Menambahkan Kamar {room_number} ({room_type})"
        else:
            return "Invalid room type."

    # Enqueue ke Data Pelanggan
    def enqueue_display_reservations(self):
        return st.session_state["reservations"]

    # Konfirmasi check-in berdasarkan nama pelanggan
    def confirm_checkin_by_name(self, guest_name, checkin_datetime):
        for reservation in st.session_state["reservations"]:
            if reservation["Nama Pelanggan"] == guest_name:
                
                # Penggunaan logika untuk waktu konfirmasi checkin
                if checkin_datetime < reservation["Check In"]:
                    return f"Check-in tidak bisa dilakukan sebelum waktu check-in ({reservation['Check In']})."
                if checkin_datetime > reservation["Check Out"]:
                    return f"Check-in tidak bisa dilakukan setelah waktu check-out ({reservation['Check Out']})."
                if reservation["Konfirmasi Check-In"]:
                    return f"Check-in sudah dikonfirmasi sebelumnya untuk {guest_name}."
                
                reservation["Konfirmasi Check-In"] = True
                reservation["Check In Telah Dikonfirmasi"] = checkin_datetime
                return f"Check-in sukses untuk {guest_name} di kamar nomor {reservation['Nomor Kamar']} pada {checkin_datetime}."

        return f"Tidak ditemukan pelanggan atas nama {guest_name}."

    # Dequeue: checkout pelanggan berdasarkan nama dan akan mengurangi Data Pelanggan
    def dequeue_checkout_guest_by_name(self, guest_name, checkout_datetime):
        late_fees = {
            "Single": 75000,
            "Standard": 100000,
            "Deluxe": 150000,
            "Suite": 250000,
            "Superior": 400000
        }

        for reservation in st.session_state["reservations"]:
            if reservation["Nama Pelanggan"] == guest_name:
                check_in_datetime = reservation["Check In"]
                original_checkout_datetime = reservation["Check Out"]
                room_type = reservation["Tipe Kamar"]

                # Penggunaan logika untuk waktu konfirmasi checkout
                if not reservation["Konfirmasi Check-In"]:
                    return "Checkout tidak bisa dilakukan karena belum di Konfirmasi check-in."
                elif checkout_datetime < check_in_datetime:
                    return f"Checkout tidak bisa dilakukan sebelum waktu checkin yaitu ({check_in_datetime})."
                elif checkout_datetime < reservation["Check In Telah Dikonfirmasi"]:
                    return f"Checkout tidak bisa dilakukan sebelum waktu check-in telah dikonfirmasi ({reservation['Check In Telah Dikonfirmasi']})."
                
                # Penggunaan logika untuk denda keterlambatan
                late_fee = 0
                if checkout_datetime > original_checkout_datetime:
                    late_days = (checkout_datetime - original_checkout_datetime).days
                    late_fee = (late_days + 1) * late_fees[room_type]

                st.session_state["reservations"].remove(reservation)
                for room in st.session_state["rooms"][room_type]:
                    if room["number"] == reservation["Nomor Kamar"]:
                        room["reserved"] = False
                        break

                reservation["Konfirmasi Checkout"] = checkout_datetime
                reservation["Denda Keterlambatan"] = late_fee
                st.session_state["checkout_history"].append(reservation)

                result_message = (f"Checkout sukses untuk {guest_name} di kamar nomor {reservation['Nomor Kamar']}. "
                                  f"Check-in: {reservation['Check In']}, Check-out: {checkout_datetime}.")
                if late_fee > 0:
                    result_message += f" Denda keterlambatan: Rp {late_fee}."
                return result_message
        return f"Tidak ditemukan pelanggan atas nama {guest_name}."

    # Menampilkan riwayat checkout
    def display_checkout_history(self):
        return st.session_state["checkout_history"]

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(image_file):
    bin_str = get_base64_of_bin_file(image_file)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Konversi data riwayat pelanggan kedalam bentuk Excel
def convert_df_to_excel(df, total_price, total_revenue, total_income):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Riwayat Pelanggan')
        workbook = writer.book
        worksheet = writer.sheets['Riwayat Pelanggan']

        # Pembuatan Kolom
        for col_num, value in enumerate(df.columns.values):
            column_len = max(df[value].astype(str).map(len).max(), len(value)) + 2
            worksheet.set_column(col_num, col_num, column_len)

        # Penambahan Format
        format_header = workbook.add_format({'bold': True, 'bg_color': 'purple', 'color': 'white', 'border': 1})
        format_cell = workbook.add_format({'border': 1})
        format_datetime = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm', 'border': 1})
        format_total = workbook.add_format({'bold': True, 'bg_color': 'yellow', 'border': 1})

        # Penambahan format ke header
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, format_header)

        for row_num, row_data in enumerate(df.values):
            for col_num, cell_data in enumerate(row_data):
                if isinstance(cell_data, pd.Timestamp):
                    worksheet.write_datetime(row_num + 1, col_num, cell_data, format_datetime)
                else:
                    worksheet.write(row_num + 1, col_num, cell_data, format_cell)

        # Penambahan baris total
        worksheet.write(len(df) + 1, 0, 'Total Pendapatan pemesanan', format_total)
        worksheet.write(len(df) + 1, len(df.columns) - 1, total_price, format_total)
        worksheet.write(len(df) + 2, 0, 'Total Denda', format_total)
        worksheet.write(len(df) + 2, len(df.columns) - 1, total_revenue, format_total)
        worksheet.write(len(df) + 3, 0, 'Total Pendapatan Keseluruhan', format_total)
        worksheet.write(len(df) + 3, len(df.columns) - 1, total_income, format_total)

    processed_data = output.getvalue()
    return processed_data

# Konversi data pelanggan kedalam bentuk Excel
def convert_reservations_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Pelanggan')
        workbook = writer.book
        worksheet = writer.sheets['Data Pelanggan']

        # Pembuatan Kolom
        for col_num, value in enumerate(df.columns.values):
            column_len = max(df[value].astype(str).map(len).max(), len(value)) + 2
            worksheet.set_column(col_num, col_num, column_len)

        # Penambahan Format
        format_header = workbook.add_format({'bold': True, 'bg_color': 'purple', 'color': 'white', 'border': 1})
        format_cell = workbook.add_format({'border': 1})
        format_datetime = workbook.add_format({'num_format': 'dd-mm-yyyy hh:mm', 'border': 1})
        
        # Penambahan format ke header
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, format_header)

        for row_num, row_data in enumerate(df.values):
            for col_num, cell_data in enumerate(row_data):
                if isinstance(cell_data, pd.Timestamp):
                    worksheet.write_datetime(row_num + 1, col_num, cell_data, format_datetime)
                else:
                    worksheet.write(row_num + 1, col_num, cell_data, format_cell)

    processed_data = output.getvalue()
    return processed_data

hotel = HotelReservation()

# Pembuatan judul aplikasi
st.title("Antrian Kamar Hotel")
with st.sidebar:
    st.markdown("## Pilih Menu") # Sidebar menu
    if st.button("🛏️ Display kamar tersedia"):
        st.session_state["menu"] = "Display kamar tersedia"
    if st.button("➕ Tambah Kamar"):
        st.session_state["menu"] = "Tambah Kamar"
    if st.button("📝 Pesan Kamar"):
        st.session_state["menu"] = "Pesan Kamar"
    if st.button("📋 Data Pelanggan"):
        st.session_state["menu"] = "Data Pelanggan"
    if st.button("🛬 Konfirmasi Check-in"):
        st.session_state["menu"] = "Konfirmasi Check-in"
    if st.button("✅ Konfirmasi Checkout"):
        st.session_state["menu"] = "Konfirmasi Checkout"
    if st.button("📜 Riwayat Pelanggan"):
        st.session_state["menu"] = "Riwayat Pelanggan"

if "menu" not in st.session_state:
    st.session_state["menu"] = "Display kamar tersedia"

option = st.session_state["menu"]

# Menu kamar tersedia
if option == "Display kamar tersedia":
    set_background('Home.jpg')  # Background menu display kamar tersedia
    st.header("Kamar Tersedia")
    available_rooms, room_prices, room_details = hotel.display_available_rooms()
    available_rooms_df = pd.DataFrame([
        {"Jenis Kamar": room_type, "Kamar Tersedia": count, "Harga": f"Rp {room_prices[room_type]:,}"}
        for room_type, count in available_rooms.items()
    ])

    room_details_flat = []
    for room_type, rooms in room_details.items():
        for room in rooms:
            status = "Tersedia"
            for reservation in st.session_state["reservations"]:
                if reservation["Nomor Kamar"] == room['number'] and reservation["Tipe Kamar"] == room_type:
                    if reservation["Konfirmasi Check-In"]:
                        status = "Telah Dipesan"
                    else:
                        status = "Booking"
                    break
            room_details_flat.append({
                "Jenis Kamar": room_type,
                "Nomor Kamar": room['number'],
                "Status": status
            })
    room_details_df = pd.DataFrame(room_details_flat)
    
    st.dataframe(available_rooms_df.style.set_properties(**{
        'background-color': 'lavender',
        'color': 'black',
        'border-color': 'white'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', 'purple'), ('color', 'white'), ('font-weight', 'bold')]}
    ]))
    st.dataframe(room_details_df.style.set_properties(**{
        'background-color': 'lavender',
        'color': 'black',
        'border-color': 'white'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', 'purple'), ('color', 'white'), ('font-weight', 'bold')]}
    ]))

# Menu menambahkan kamar tersedia
elif option == "Tambah Kamar":
    set_background('Add.jpg') # Background menu penambahan kamar tersedia
    st.header("Tambah Kamar")
    room_type = st.selectbox("Jenis Kamar", ["Single", "Standard", "Deluxe", "Suite", "Superior"])
    room_number = st.text_input("Nomor Kamar")
    if st.button("Tambah Kamar"):
        result = hotel.enqueue_add_room(room_type, room_number)
        st.success(result)

# Menu pemesanan kamar
elif option == "Pesan Kamar":
    set_background('Buy.jpg') # Background menu pemesanan kamar
    st.header("Pesan Kamar")
    room_type = st.selectbox("Jenis Kamar", ["Single", "Standard", "Deluxe", "Suite", "Superior"])
    guest_name = st.text_input("Nama Pelanggan")
    guest_phone = st.text_input("Nomor Telepon Pelanggan")
    check_in_date = st.date_input("Tanggal Check In", date.today())
    check_in_time = st.time_input("Waktu Check In", time(8, 0))
    check_out_date = st.date_input("Tanggal Check Out", date.today())
    check_out_time = st.time_input("Waktu Check Out", time(23, 0))
    check_in_datetime = datetime.combine(check_in_date, check_in_time)
    check_out_datetime = datetime.combine(check_out_date, check_out_time)
    payment_method = st.selectbox("Metode Pembayaran", ["Tunai", "Kartu Kredit", "Kartu Debit", "Transfer Bank"])
    
    # Penggunaan logika pemesanan kamar
    if st.button("Pesan Kamar"):

        # Penggunaan logika untuk input data pemesan
        if not guest_name and guest_phone:
            st.error("Nama pelanggan harus diisi!")
        elif not guest_phone and guest_name:
            st.error("Nomor pelanggan harus diisi!")
        elif not guest_name or not guest_phone:
            st.error("Nama pelanggan dan nomor telepon harus diisi!")
        elif not guest_name.replace(" ", "").isalpha() and guest_phone.isdigit():
            st.error("Nama pelanggan harus berupa huruf.")
        elif not guest_phone.isdigit() and guest_name.replace(" ", "").isalpha():
            st.error("Nomor telepon harus berupa angka.")
        elif not guest_name.replace(" ", "").isalpha() or not guest_phone.isdigit():
            st.error("Nama pelanggan harus berupa huruf dan Nomor telepon harus berupa angka.")
        elif len(guest_phone) < 12:
            st.error("Nomor telepon minimal 12 digit.")
        elif check_out_date <= check_in_date:
            st.error("Tanggal check-out tidak boleh sebelum atau sama dengan tanggal check-in.")
        else:
            reservation = hotel.dequeue_reservation(room_type, guest_name, guest_phone, check_in_datetime, check_out_datetime, payment_method)
            if reservation:
                st.success(f"Kamar {reservation['Nomor Kamar']} telah dipesan oleh {guest_name}.")
                pdf_data = hotel.generate_reservation_pdf(reservation)  # Pembuatn pdf ketika pemesanan berhasil
                st.download_button(label="Cetak Bukti Pemesanan", data=pdf_data, file_name=f"Bukti_Pemesanan_{guest_name}.pdf", mime="application/pdf")
            else:
                st.error(f"Maaf, tidak tersedia kamar {room_type}.")

# Menu data pelanggan
elif option == "Data Pelanggan":
    set_background('Information.jpg')
    st.header("Data Pelanggan")
    reservations_df = pd.DataFrame(hotel.enqueue_display_reservations())
    if not reservations_df.empty:
        reservations_df["Lama (Hari)"] = reservations_df.apply(lambda row: (row["Check Out"] - row["Check In"]).days, axis=1)
        reservations_df["Konfirmasi Check-In"] = reservations_df["Konfirmasi Check-In"].apply(lambda x: "✔️" if x else "❌")
        reservations_df["Total Harga"] = reservations_df["Total Harga"].apply(lambda x: f"Rp {x:,}")  # Format Rp

        # Pemanggilan untuk kolom
        columns_order = ["Nomor Kamar", "Tipe Kamar", "Nama Pelanggan", "Nomor Telepon", "Check In", "Check Out", "Check In Telah Dikonfirmasi", "Konfirmasi Check-In", "Lama (Hari)",  "Total Harga", "Metode Pembayaran"]
        reservations_df = reservations_df[columns_order]

        st.dataframe(reservations_df.style.set_properties(**{
            'background-color': 'lavender',
            'color': 'black',
            'border-color': 'white'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', 'purple'), ('color', 'white'), ('font-weight', 'bold')]}
        ]))
        
        # Ekspor kedalam bentuk excel
        excel_data = convert_reservations_to_excel(reservations_df)
        st.download_button(label="Download Data Pelanggan", data=excel_data, file_name="Data_Pelanggan.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Belum ada reservasi.")

# Menu konfirmasi checkin
elif option == "Konfirmasi Check-in":
    set_background('Check.png')
    st.header("Konfirmasi Check-in")
    guest_name = st.text_input("Nama Pelanggan untuk Konfirmasi Check-in")
    checkin_date = st.date_input("Tanggal", date.today())
    checkin_time = st.time_input("Waktu", time(12, 0))
    checkin_datetime = datetime.combine(checkin_date, checkin_time)
    if st.button("Konfirmasi Check-in"):
        result = hotel.confirm_checkin_by_name(guest_name, checkin_datetime)
        st.success(result)

# Menu konfirmasi checkout
elif option == "Konfirmasi Checkout":
    set_background('Out.jpg')
    st.header("Konfirmasi Checkout")
    guest_name = st.text_input("Nama Pelanggan untuk Konfirmasi Checkout")
    checkout_date = st.date_input("Tanggal Checkout Sebenarnya", date.today())
    checkout_time = st.time_input("Waktu Checkout Sebenarnya", time(14, 0))
    checkout_datetime = datetime.combine(checkout_date, checkout_time)
    if st.button("Konfirmasi Checkout"):
        result = hotel.dequeue_checkout_guest_by_name(guest_name, checkout_datetime)
        st.success(result)

# Menu riwayat pelanggan
elif option == "Riwayat Pelanggan":
    set_background('History.jpg')
    st.header("Riwayat Pelanggan")
    checkout_history_df = pd.DataFrame(hotel.display_checkout_history())
    if not checkout_history_df.empty:
        checkout_history_df = checkout_history_df.drop(columns=["Konfirmasi Check-In"])

        # Tambahkan format "Rp" pada kolom "Total Harga" dan "Denda Keterlambatan"
        checkout_history_df["Total Harga"] = checkout_history_df["Total Harga"].apply(lambda x: f"Rp {x:,}")
        checkout_history_df["Denda Keterlambatan"] = checkout_history_df["Denda Keterlambatan"].apply(lambda x: f"Rp {x:,}")

        st.dataframe(checkout_history_df.style.set_properties(**{
            'background-color': 'lavender',
            'color': 'black',
            'border-color': 'white'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', 'purple'), ('color', 'white'), ('font-weight', 'bold')]}
        ]))
        
        # Hitung total harga dari pesanan kamar (Total Harga)
        total_price = checkout_history_df["Total Harga"].apply(lambda x: int(x.replace('Rp ', '').replace(',', ''))).sum()
        
        # Hitung total denda keterlambatan (Denda Keterlambatan)
        total_revenue = checkout_history_df["Denda Keterlambatan"].apply(lambda x: int(x.replace('Rp ', '').replace(',', ''))).sum()
        
        # Hitung total pendapatan keseluruhan
        total_income = total_price + total_revenue
        
        st.markdown(f"**Total Pendapatan Keseluruhan: Rp {total_income:,}**")
        st.markdown(f"**Total Pendapatan Pemesanan: Rp {total_price:,}**")
        st.markdown(f"**Total Denda: Rp {total_revenue:,}**")

        # Ekspor kedalam bentuk excel
        excel_data = convert_df_to_excel(checkout_history_df, total_price, total_revenue, total_income)
        st.download_button(label="Download Riwayat Pelanggan", data=excel_data, file_name="Riwayat_Pelanggan.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("Belum ada riwayat pelanggan.")