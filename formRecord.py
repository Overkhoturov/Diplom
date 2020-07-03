from __future__ import print_function
import pyaudio
import wave
from tkinter import *
from tkinter import messagebox 
import scipy.io.wavfile as wavfile
import scipy
import scipy.fftpack
import numpy as np
from matplotlib import pyplot as plt
import vg
import pyodbc
from fuzzywuzzy import fuzz 

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 2

def Levenshtein(s1, s2):
    return fuzz.token_sort_ratio(s1, s2)

def tanimoto(s1, s2):
    a, b, c = len(s1), len(s2), 0.0
    for sym in s1:
        if sym in s2:
            c += 1
    return c / (a + b - c)

def fourier(signal):
    FFT = abs(scipy.fft.fft(signal))
    return FFT

def draw(WAVE_OUTPUT_FILENAME):
    fs_rate,signal = wavfile.read(WAVE_OUTPUT_FILENAME)
    print ("Frequency sampling", fs_rate)
    l_audio = len(signal.shape)
    print ("Channels", l_audio)
    if l_audio == 2:
        signal = signal.sum(axis=1) / 2
    N = signal.shape[0]
    print ("Complete Samplings N", N)
    secs = N / float(fs_rate)
    print ("secs", secs)
    Ts = 1.0/fs_rate 
    print ("Timestep between samples Ts", Ts)
    t = np.arange(0, secs, Ts) 
    FFT = abs(scipy.fft.fft(signal))

    freqs = scipy.fftpack.fftfreq(signal.size, t[1]-t[0])
    fft_freqs = np.array(freqs)

    plt.subplot(311)
    p1 = plt.plot(t, signal, "g")
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.subplot(313)
    p2 = plt.plot(freqs, FFT, "r")
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Count dbl-sided')
    plt.show()

def clickedRec(WAVE_OUTPUT_FILENAME):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")
    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def clickedRegis():

    def BDReg():
        cnxn = pyodbc.connect('Driver={SQL Server};Server=DESKTOP-0UFPAFV\SQLEXPRESS;'+
        'Database=for_diplom;Trusted_Connection=yes;')
        cursor = cnxn.cursor()
        cursor.execute("insert into registr_data(name, password) values ('" + name_entry.get() + "','"+ password_entry.get() +"' )")
        cnxn.commit()
        cnxn.close()

    WAVE_OUTPUT_FILENAME = "output1.wav"

    window = Tk()  
    window.title("Регистрация")  
    window.geometry('600x450')  

    name_label = Label(window, text="Введите имя", font=("Arial Bold", 15))
    name_label.place(relx=.25, rely=.4, anchor="c")

    name = StringVar()
    password = StringVar()

    name_entry = Entry(window,width=20,textvariable = name)
    name_entry.place(relx=.5, rely=.4, anchor="c") 

    password_label = Label(window, text="Введите пароль", font=("Arial Bold", 15))
    password_label.place(relx=.25, rely=.5, anchor="c") 

    password_entry = Entry(window,width=20, textvariable = password, show = "*")
    password_entry.place(relx=.5, rely=.5, anchor="c")
    

    btnRecRegis = Button(window, text="Записать голос", padx="30", command = lambda: clickedRec(WAVE_OUTPUT_FILENAME))  
    btnRecRegis.place(relx=.5, rely=.6, anchor="c", height=30, width=130, bordermode=OUTSIDE)

    btnShowGraph = Button(window, text="Показать графики сигналов", padx="30", command = lambda: draw(WAVE_OUTPUT_FILENAME))  
    btnShowGraph.place(relx=.75, rely=.6, anchor="c", height=30, width=170, bordermode=OUTSIDE)

    btnBDReg = Button(window, text="Регистрация", padx="30", command = BDReg)  
    btnBDReg.place(relx=.85, rely=.5, anchor="c", height=30, width=130, bordermode=OUTSIDE)

    window.mainloop()

def clickedSign():

    def BDSign():
        windowSigned = Tk()
        windowSigned.title("Профиль")
        windowSigned.geometry('600x450')
        name = name_entry.get()
        password = password_entry.get()

        cnxn = pyodbc.connect('Driver={SQL Server};Server=DESKTOP-0UFPAFV\SQLEXPRESS;'+
        'Database=for_diplom;Trusted_Connection=yes;')
        cursor = cnxn.cursor()
        cursor.execute("select name, password from registr_data")

        loggedName =''    
        rows = cursor.fetchall()
        for row in rows:
            if (row.name == name and row.password == password):
                loggedName = row.name
        cnxn.commit()
        cnxn.close()

        if loggedName == '':
            messagebox.showinfo("Ошибка","Введенное имя или пароль не верны")
            name_label = Label(windowSigned, text="Доступ запрещен" , font=("Arial Bold", 15))
            name_label.place(relx=.5, rely=.4, anchor="c")
        else:
            name_label = Label(windowSigned, text="Вы вошли как пользователь" +" "+loggedName , font=("Arial Bold", 15))
            name_label.place(relx=.5, rely=.4, anchor="c")

            btnCheck = Button(windowSigned, text="Сравнить голоса", padx="30", command = lambda: clickedMatching())  
            btnCheck.place(relx=.5, rely=.75, anchor="c", height=30, width=130, bordermode=OUTSIDE)

            windowSigned.mainloop()
    
    WAVE_OUTPUT_FILENAME = "output2.wav"

    window = Tk()  
    window.title("Вход")  
    window.geometry('600x450')  

    name_label = Label(window, text="Введите имя", font=("Arial Bold", 15))
    name_label.place(relx=.25, rely=.4, anchor="c")

    name = StringVar()
    password = StringVar()

    name_entry = Entry(window,width=20,textvariable = name)
    name_entry.place(relx=.5, rely=.4, anchor="c") 

    password_label = Label(window, text="Введите пароль", font=("Arial Bold", 15))
    password_label.place(relx=.25, rely=.5, anchor="c") 

    password_entry = Entry(window,width=20, textvariable = password, show = "*")
    password_entry.place(relx=.5, rely=.5, anchor="c")

    btnRecAuth = Button(window, text="Записать голос(пров)", padx="30", command = lambda: clickedRec(WAVE_OUTPUT_FILENAME))  
    btnRecAuth.place(relx=.5, rely=.6, anchor="c", height=30, width=130, bordermode=OUTSIDE)

    btnShowGraph = Button(window, text="Показать графики сигналов", padx="30", command = lambda: draw(WAVE_OUTPUT_FILENAME))  
    btnShowGraph.place(relx=.75, rely=.6, anchor="c", height=30, width=170, bordermode=OUTSIDE)

    btnBDReg = Button(window, text="Вход", padx="30", command = BDSign)  
    btnBDReg.place(relx=.85, rely=.5, anchor="c", height=30, width=130, bordermode=OUTSIDE)
    window.mainloop()

def clickedMatching():
    fs_rateFirst,signalFirst = wavfile.read("output1.wav")
    fs_rateSecond,signalSecond = wavfile.read("output2.wav")
    print ("Frequency sampling", fs_rateFirst, ",", fs_rateSecond)
    l_audioFirst = len(signalFirst.shape)
    l_audioSecond = len(signalSecond.shape)
    print ("Channels", l_audioFirst)
    if l_audioFirst == 2 & l_audioFirst == 2:
        signalFirst = signalFirst.sum(axis=1) / 2
        signalSecond = signalSecond.sum(axis=1) / 2
    
    FFTFirst = abs(scipy.fft.rfft(signalFirst))
    FFTSecond = abs(scipy.fft.rfft(signalSecond))
    norm1 = np.round_(vg.normalize(FFTFirst),7)
    norm2 = np.round_(vg.normalize(FFTSecond),7)
    tani = np.round_ (tanimoto(
        norm1,
        norm2,
    ),3)
    livenshtein = Levenshtein(
        norm1,
        norm2,
    )
    messagebox.showinfo("Результаты сравнения", "Коэффициент Танимото:" + str(tani*100) + "%" + "\n"+
    "\n" + "Расстояние Левенштейна:" + str(livenshtein) + "%")

    print("Коэффициент Танимото:", tani*100, "%")
    print("Расстояние Левенштейна:", livenshtein, "%")

window = Tk() 
window.title("Система аутентификации")  
window.geometry('600x450')

mainLabel = Label(window, text="Система аутентификации пользователей \n по голосу ", justify = CENTER, font=("Arial Bold", 15))  
mainLabel.place(relx=.5, rely=.15, anchor="c")

btnRegis = Button(window, text="Регистрация", command=clickedRegis)  
btnRegis.place(relx=.25, rely=.5, anchor="c", height=30, width=130, bordermode=OUTSIDE) 

btnSign = Button(window, text="Вход", command=clickedSign)  
btnSign.place(relx=.75, rely=.5, anchor="c", height=30, width=130, bordermode=OUTSIDE)
window.mainloop()
