import pickle
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from sklearn.feature_extraction.text import TfidfVectorizer
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode
from pymongo import MongoClient

# Inisialisasi MongoDB Atlas
uri = st.secrets["KEYMONG"]  # Inisialisasi Secret Key Database
client = MongoClient(uri)
db = client["DatabaseSMS"]

# Load saved model and vectorizer
@st.cache_resource
def load_model_and_vectorizer():
    model = pickle.load(open('Model/model_spam.sav', 'rb'))
    vocab = pickle.load(open("Model/new_selected_feature_tf-idf.sav", "rb"))
    vectorizer = TfidfVectorizer(decode_error="replace", vocabulary=set(vocab))
    # Fit the vectorizer with dummy data to avoid NotFittedError
    vectorizer.fit(["dummy data"])
    return model, vectorizer

model_spam, loaded_vec = load_model_and_vectorizer()

# Function to load detection results from MongoDB
def load_detection_results(collection_name):
    collection = db[collection_name]
    results = collection.find()
    data = [{'SMS': result.get('SMS'), 'Keterangan': result.get('Keterangan')} for result in results]
    return pd.DataFrame(data)

# Function to save detection results to MongoDB
def save_detection_results(sms_text, prediction, collection_name):
    collection = db[collection_name]
    result = {'SMS': sms_text, 'Keterangan': prediction}
    try:
        collection.insert_one(result)
        
    except Exception as e:
        st.write(f"Gagal menyimpan data ke MongoDB untuk koleksi {collection_name}:", e)

# Sidebar dengan option menu
with st.sidebar:
    page = option_menu(
        "Menu Navigasi",
        ["Informasi SMS Spam", "Panduan Aplikasi", "Aplikasi Deteksi SMS", "List Hasil Deteksi", "Tentang Saya"],
        icons=["info-circle", "book", "search", "table", "person"],
        menu_icon="cast",
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": "#68ADFF", "color": "white"},
        },
    )
    st.markdown(
        """
        <div style="margin-top: 190px;">
            <strong>Versi Aplikasi:</strong> 1.0.0
        <br>
        <small>&copy; 2024 by Kevin</small>
        </div>
        """,
        unsafe_allow_html=True
    )

# Halaman Tentang SMS Spam
if page == "Informasi SMS Spam":
    #ARTIKEL KE-1
    st.title('Apasih SMS Spam itu?')
    st.markdown(
        """
        <div style="text-align: justify;">
            Kalian pernah bertanya-tanya sebenernya SMS spam itu apasih?apakah berbahaya?.Weets,tenang dulu ya gess karena disini saya akan membahas lebih lanjut tentang topik ini,let's gooo.
            Secara umum SMS spam ialah sebuah pesan teks yang tidak diinginkan yang dikirim secara massal kepada banyak penerima.
            Pesan ini sering kali berisi penawaran promosi, penipuan, atau informasi yang tidak relevan. SMS spam dapat mengganggu dan menghabiskan sumber daya pada perangkat penerima.
            Maka dari itu dengan teknologi deteksi SMS spam, kita dapat memfilter dan mengelompokkan pesan-pesan ini untuk mengurangi dampak negatifnya.

        </div>
        <br><br><br>
        """,
        unsafe_allow_html=True
    )
    st.image("Assets/spamsms.png", caption="Gambar SMS spam", use_column_width=True)
    st.write("<br><br>", unsafe_allow_html=True)

    #ARTIKEL KE-2
    st.title('Jenis Dan Tujuan SMS Spam')
    st.image("Assets/notification.gif",caption="Animasi notifikasi masuk", use_column_width=True)
    st.write("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: justify;">
            Berdasarkan penjelasan tentang arti spam yang telah disampaikan, berikut adalah beberapa tujuan spam yang perlu kita ketahui:
        <br>
        <h3>1. Skema Penipuan</h3>
        <p>Beberapa SMS spam dirancang untuk menipu penerima. Misalnya, pesan dapat mengklaim bahwa penerima telah memenangkan hadiah atau undian, meminta mereka untuk membayar biaya untuk mengklaim hadiah tersebut. Ini bisa berujung pada kerugian finansial bagi penerima.</p>

        <h3>2. Phishing</h3>
        <p>SMS phishing berusaha mendapatkan informasi sensitif, seperti nomor kartu kredit atau kata sandi. Pesan ini mungkin mengarahkan penerima ke situs web palsu yang terlihat mirip dengan situs resmi, di mana mereka diminta untuk memasukkan informasi pribadi.</p>

        <h3>3. Jenis Iklan Yang Menggangu</h3>
        <p>Banyak bisnis menggunakan SMS spam untuk mengirimkan iklan tanpa izin penerima. Ini sering kali dianggap sebagai gangguan dan dapat merusak reputasi pengirim.</p>

        <h3>4. Penawaran Jasa Keuangan</h3>
        <p>Beberapa pesan menawarkan layanan keuangan, seperti pinjaman atau investasi. Banyak dari layanan ini mungkin tidak sah atau memiliki syarat yang merugikan.</p>
        </div>
        
        """,
        unsafe_allow_html=True
    )
    st.write("<br><br>", unsafe_allow_html=True)

    #ARTIKEL KE-3
    st.title('Dampak Buruk SMS Spam')
    st.image("Assets/thinking.gif",caption="Animasi memikirkan jenis pesan",use_column_width=True)
    st.markdown(
        """
        <div style="text-align: justify;">
            Seperti yang kita ketahui bahwa pesan SMS yang kita terima memiliki berbagai jenis pesan-pesan yang masuk.Namun kalian tau ngga gess? Bahwasanya dari semua pesan yang masuk itu sudah tidak dipungkiri lagi terdapat jenis pesan spam.Terus emangnya kenapa min?
            kan itu hanya sebuah teks pesan saja?.Yup… kalian bener sekali itu hanya sebuah teks pesan biasa saja, tapi dibalik pesan spam yang masuk itu diiantaranya memiliki dampak yang buruk jika kita selalu waspada akan isi pesan tersebut.
        <br><br>

        Belum lagi banyaknya modus penipuan yang hanya dikirim melalui SMS, oleh karena itu mimin hanya ingin menyampaikan beberapa dampak buruk SMS spam pada perorangan, diantaranya sebagai berikut ini:
        <br>
        <ol>
            <li>Spam sering digunakan untuk phishing, di mana penipu mencoba mendapatkan informasi pribadi seperti nomor kartu kredit, kata sandi, dan data sensitif lainnya.</li>
            <li>Beberapa spam berisi tautan atau lampiran yang mengandung malware, yang dapat menginfeksi perangkat penerima dan mencuri data pribadi.</li>
            <li>Individu yang tertipu oleh spam yang menjanjikan hadiah, lotere, atau tawaran keuangan palsu bisa mengalami kerugian finansial yang signifikan.</li>
            <li>Spam yang menggunakan identitas seseorang untuk mengirim pesan dapat merusak hubungan pribadi jika penerima merasa terganggu atau terancam.</li>
            <li>Menggunakan sumber daya perangkat elektronik secara berlebihan sehingga mengurangi efisiensi penggunaannya.</li>
        </ol>
        </div>
        
        """,
        unsafe_allow_html=True
    )
    
    
# Halaman Panduan Aplikasi
elif page == "Panduan Aplikasi":
    st.title('Langkah-Langkah Penggunaan Aplikasi')
    st.write("<br>", unsafe_allow_html=True)
    #LANGKAH 1
    st.markdown(
        """
        <div style="text-align: justify;">
            Agar kalian tidak kebingungan cara menggunakan aplikasi deteksinya  mimin akan kasih tau nih biar kalian ngga kebingungan.Sebenernya simple sih, tapi tidak apa-apa biar kalian paham dan sekalian baca-baca😁.Nah kalau begitu berikut langkah-langkah penggunaan aplikasi:
        <br><br>
        <ol start="1">
        <li>Untuk memulai cara penggunaan aplikasi deteksi spam,langkah pertama kita pilih menu pada bagian “Aplikasi Deteksi SMS” pada halaman sidebar menu navigasi dan kita dapat melihat sebuah tampilan dari sistem deteksi SMS spam seperti gambar dibawah ini:</p>
        </li>
        <br>
        """,
        unsafe_allow_html=True
    )
    st.image("Assets/LANGKAH1.PNG",caption="Gambar panduan pertama",use_column_width=True)

    #LANGKAH 2
    st.markdown(
        """
        <br><br>
        <div style="text-align: justify;">
        <ol start="2">
        <li>Kemudian sekarang kita akan memasukkan sebuah teks pesan SMS kita yang ada di HP kita masing-masing dengan cara copy and paste ke area input-text area halaman deteksi.Setelah kalian sudah menginput teks yang kalian pilih, kemudian tekan tombol “Deteksi” untuk melihat hasil output yang akan ditampilkan seperti gambar dibawah ini:</p>
        </li>
        <br>
        """,
        unsafe_allow_html=True
    )
    st.image("Assets/LANGKAH2.PNG",caption="Gambar panduan kedua",use_column_width=True)

    #LANGKAH 3
    st.markdown(
        """
        <br><br>
        <div style="text-align: justify;">
        <ol start="3">
        <li>Yeyy, sudah deh.Hasil deteksi pesan yang tadi sudah kita input menunjukkan bahwa pesan tersebut merupakan jenis SMS normal yang artinya aman untuk direspon/ditanggapi dan tidak ada terindikasi bahwa pesan tersebut spam.</p>
        </li>
        <br>
        """,
        
        unsafe_allow_html=True
    )
    st.image("Assets/LANGKAH3.PNG",caption="Gambar hasil deteksi",use_column_width=True)

    #LANGKAH 4
    st.markdown(
        """
        <br><br>
        <div style="text-align: justify;">
        <ol start="4">
        <li>Nah jika kalian sudah mengujicoba hasil deteksi tersebut, hasil data-data inputan teks pesan akan dimasukkan kebagian tabel hasil deteksi pada submenu "Hasil List Deteksi" dengan tujuan untuk mengumpulkan informasi agar kedepanya mimin dapat mengupgrade model sistem deteksi SMS spam ini.
        Untuk lebih lanjut hasil simpan deteksi dapat dilihat pada gambar dibawah ini:</p>
        </li>
        <br>
        </ol>
        """,
        
        unsafe_allow_html=True
    )
    st.image("Assets/LANGKAH4.PNG",caption="Gambar penyimpanan hasil deteksi",use_column_width=True)

    #LANGKAH 5
    st.markdown(
        """
        <br><br>
        <div style="text-align: justify;">
        <p>Terus min tampilan pesan spamnya seperti apa?Tenang kok, untuk tampilan yang terindikasi SMS spam ada.Namun mimin sengaja ngga menampilkan hasil deteksi tersebut pada panduan ini agar kalian dapat mengujicoba nya dan melihatnya secara langsung.Sekian panduan penggunaan aplikasi deteksi SMS spam, Selamat mencoba…</p>
        <br>
        """,
        unsafe_allow_html=True
    )

# Halaman Aplikasi Deteksi
elif page == "Aplikasi Deteksi SMS":
    st.title('Sistem Deteksi SMS Spam')

    st.markdown(
        """
        <style>
        textarea {
            font-size: 20px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    sms_text = st.text_area("Masukkan Teks SMS Dibawah Ini")
    if st.button('Cek Deteksi'):
        clean_teks = sms_text.strip()

        if clean_teks == "":
            spam_detection = "Mohon Masukkan Pesan Teks SMS"
            st.markdown(
                f"""
                <div style="border: 2px; border-radius: 15px; padding: 2px; display: flex; align-items: center; background-color: #1F211D;">
                    <div style="color: #F1C40F; font-size: 25px; margin-left: 10px;"><strong>{spam_detection}</strong></div>
                    <iframe src="https://lottie.host/embed/c006c08e-3a86-47e6-aaae-3e11674c204b/cQiwVs5lkD.json" style="width: 100px; height: 100px;"></iframe>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            transformed_text = loaded_vec.transform([clean_teks])
            predict_spam = model_spam.predict(transformed_text)

            if predict_spam == 0:
                spam_detection = "SMS NORMAL"
                st.markdown(
                    f"""
                    <div style="border: 2px solid #177233; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #D6F9B7;">
                        <div style="flex: 1;">
                            <div style="color: #177233; font-size: 25px; margin-left: 10px;">
                                <strong>{spam_detection}</strong>
                            </div>
                            <div style="background-color: white; border-radius: 5px; padding: 5px; margin-top: 10px;">
                                <ul style="color: #177233; font-size: 18px; list-style-type: none; padding: 0; margin: 0;">
                                    <li>Pesan SMS ini bukan termasuk pesan spam promo/penipuan</li>
                                    <li>melainkan pesan normal pada umumnya dan aman untuk ditanggapi</li>
                                </ul>
                            </div>
                        </div>
                        <iframe src="https://lottie.host/embed/94ef5ba2-ff8e-4b1a-868b-6a6a926cfca0/D3oNNvId2Y.json" style="width: 120px; height: 120px;"></iframe>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                save_detection_results(clean_teks, spam_detection, "hasil_deteksi_normal")

            elif predict_spam == 1:
                spam_detection = "SMS PENIPUAN"
                st.markdown(
                    f"""
                    <div style="border: 2px solid #D90000; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #FF9590;">
                        <div style="flex: 1;">
                            <div style="color: #D90000; font-size: 25px; margin-left: 10px;">
                                <strong>{spam_detection}</strong>
                            </div>
                            <div style="background-color: white; border-radius: 5px; padding: 5px; margin-top: 10px;">
                                <ul style="color: #F00B00; font-size: 18px; list-style-type: none; padding: 0; margin: 0;">
                                    <li>Pesan SMS ini terindikasi pesan spam penipuan</li>
                                    <li>dikarenakan terdapat informasi yang mencurigakan</li>
                                </ul>
                            </div>
                        </div>
                        <iframe src="https://lottie.host/embed/66044930-6b4e-4546-9765-4fcf4a98ca37/U6WsPr1BHE.json" style="width: 120px; height: 120px;"></iframe>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                save_detection_results(clean_teks, spam_detection, "hasil_deteksi_penipuan")

            elif predict_spam == 2:
                spam_detection = "SMS PROMO"
                st.markdown(
                    f"""
                    <div style="border: 2px solid #3773D6; border-radius: 15px; padding: 10px; display: flex; align-items: center; background-color: #C3E6FF;">
                        <div style="flex: 1;">
                            <div style="color: #3773D6; font-size: 25px; margin-left: 10px;">
                                <strong>{spam_detection}</strong>
                            </div>
                            <div style="background-color: white; border-radius: 5px; padding: 5px; margin-top: 10px;">
                                <ul style="color: #3773D6; font-size: 18px; list-style-type: none; padding: 0; margin: 0;">
                                    <li>Pesan SMS ini adalah spam promo yang menawarkan penawaran khusus</li>
                                    <li>untuk membeli/menggunakan promo yang diberikan</li>
                                </ul>
                            </div>
                        </div>
                        <iframe src="https://lottie.host/embed/62ea7f76-6873-4024-9081-cd6cdf8a7246/amgyWxn0IT.json" style="width: 120px; height: 120px;"></iframe>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                save_detection_results(clean_teks, spam_detection, "hasil_deteksi_promo")

# Halaman Tabel Dataset
elif page == "List Hasil Deteksi":
    st.title('Tabel Hasil Deteksi SMS')

    dataset_type = st.selectbox(
        "Pilih Jenis Hasil Deteksi Dataset",
        ["Dataset Promo", "Dataset Penipuan", "Dataset Normal"]
    )

    if dataset_type == "Dataset Promo":
        filtered_data = load_detection_results("hasil_deteksi_promo")
    elif dataset_type == "Dataset Penipuan":
        filtered_data = load_detection_results("hasil_deteksi_penipuan")
    elif dataset_type == "Dataset Normal":
        filtered_data = load_detection_results("hasil_deteksi_normal")

    filtered_data.reset_index(drop=True, inplace=True)
    filtered_data.index = filtered_data.index + 1

    gb = GridOptionsBuilder.from_dataframe(filtered_data)
    gridOptions = gb.build()

    AgGrid(filtered_data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED)

    csv = filtered_data.to_csv().encode('utf-8')
    st.download_button(
        label="Unduh Dataset",
        data=csv,
        file_name=f'{dataset_type.lower().replace(" ", "_")}_data.csv',
        mime='text/csv',
    )

# Halaman Tentang Saya
elif page == "Tentang Saya":
    st.image("Assets/profile2.png", caption="Profile Pembuat Program", use_column_width=True)

# Footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: calc(100% - 20rem);
        margin-left: -5rem;
        background-color: #7DB8FF;
        color: black;
        text-align: center;
        padding: 5px 0;
        height: 50px;
        font-size: 14px;
        border-top: 2px solid #e0e0e0;
        z-index: 1000;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    @media (max-width: 2500px) {
        .footer {
            width: 100%;
            margin-left: 0;
        }
    }
    .minimized-sidebar .footer {
        width: 100%;
        margin-left: 0;
    }
    </style>
    <div class="footer"></div>
    """,
    unsafe_allow_html=True
)
