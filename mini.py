import tkinter as tk
import sqlite3
import datetime
from tkinter import ttk
# import re
# from playsound import playsound

factor = 2
num = 0
sum = 0
# connect to db
conn = sqlite3.connect('word_database.db')
cursor = conn.cursor()

# create db
cursor.execute('''
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY,
        word TEXT NOT NULL,
        meaning TEXT NOT NULL,
        last_reviewed DATE,
        next_review DATE,
        interval INTEGER,
        right INTEGER,
        wrong INTEGER,
        flag INTEGER
    )
''')
conn.commit()


def insert_word(word, meaning):
    cursor.execute('SELECT id FROM words WHERE word = ? OR meaning = ?', (word, meaning))
    existing_word = cursor.fetchone()

    if existing_word is not None:
        print("Word or meaning already exists. Not adding it.")
        return

    cursor.execute('INSERT INTO words (word, meaning, last_reviewed, next_review, interval, right, wrong, flag) VALUES \
                    (?, ?, ?, ?, ?, ?, ?, ?)',(word, meaning, datetime.date.today(), datetime.date.today(), 1, 0, 0, 0))
    conn.commit()


def get_next_word():
    # cursor.execute('SELECT * FROM words')
    # all_words = cursor.fetchall()
    # print(all_words)
    cursor.execute('SELECT * FROM words WHERE flag > 0 OR next_review <= ? ORDER BY flag ASC LIMIT 1',
                   (datetime.date.today(),))

    # cursor.execute('SELECT * FROM words ORDER BY RANDOM() LIMIT 1;')

    return cursor.fetchone()


def update_word(word_id, interval, right, wrong, flag):
    next_review = datetime.date.today() + datetime.timedelta(days=interval)

    cursor.execute('UPDATE words SET last_reviewed = ?, next_review = ?, interval = ?, right = ?, wrong = ?, flag = ? WHERE id = ?',
                   (datetime.date.today(), next_review, interval, right, wrong, flag, word_id))
    conn.commit()


def show_word_main():
    global current_word, num, sum

    cursor.execute('SELECT COUNT(*) FROM words WHERE flag > 0 OR next_review <= ?', (datetime.date.today(),))
    num = cursor.fetchall()[0][0]
    cursor.execute('SELECT COUNT(*) FROM words')
    sum = cursor.fetchall()[0][0]

    current_word = get_next_word()
    if current_word:
        word_label_main.config(text=current_word[1])
        meaning_label_main.config(text='')
        analysis.config(text='{}/{}'.format(num, sum))
        word_label_main.grid(row=1, column=2, padx=5, pady=5)
        meaning_label_main.grid(row=3, column=2, padx=5, pady=5)
        show_button.grid(row=10, column=2, padx=5, pady=5)
        add_word_button.grid(row=0, column=0, padx=5, pady=5)
        view_all_words_button.grid(row=0, column=4, padx=5, pady=5)
        analysis.grid(row=10, column=4)
    else:
        word_label_main.config(text="No Word Needs to be Recited!")
        meaning_label_main.config(text='')
        analysis.config(text='{}/{}'.format(num, sum))
        word_label_main.grid(row=1, column=2, padx=5, pady=5)
        meaning_label_main.grid(row=3, column=2, padx=5, pady=5)
        show_button.grid(row=10, column=2, padx=5, pady=5)
        add_word_button.grid(row=0, column=0, padx=5, pady=5)
        view_all_words_button.grid(row=0, column=4, padx=5, pady=5)
        analysis.grid(row=10, column=4)


# def split_phrase(sentence):
#     words = re.findall(r'\b\w+(?:-\w+)*\b', sentence)
#     return words


def show_word_show():
    global current_word
    if current_word:

        # try:
        #     parts = split_phrase(current_word[2])
        #     print(parts)
        #     for part in parts:
        #         audio_url = 'https://ssl.gstatic.com/dictionary/static/sounds/oxford/{}--_gb_1.mp3'.format(part.lower())
        #         playsound(audio_url)
        # except:
        #     pass

        word_label.config(text=current_word[1])
        meaning_label.config(text=current_word[2])
        word_label.grid(row=1, column=2, padx=5, pady=1)
        meaning_label.grid(row=3, column=2, padx=5, pady=1)
        next_button.grid(row=5, column=4, padx=5, pady=5)
        forgot_button.grid(row=5, column=0, padx=5, pady=5)
    else:
        word_label.config(text="No Word Needs to be Recited!")
        meaning_label.config(text=" ")
        word_label.grid(row=1, column=2, padx=5, pady=1)
        meaning_label.grid(row=3, column=2, padx=5, pady=1)
        next_button.grid(row=5, column=4, padx=5, pady=5)
        forgot_button.grid(row=5, column=0, padx=5, pady=5)


def next_word(event=None):
    try:
        if current_word[8] == 0:
            global factor
            interval = current_word[5] * factor if current_word[3] != current_word[4] else 1
            interval = 30 if interval >= 30 else interval
            update_word(current_word[0], interval, current_word[6] + 1, current_word[7], 0)
        else:
            update_word(current_word[0], 1, current_word[6] + 1, current_word[7], 0)
        show_word_screen()
    except:
        show_word_screen()


def forgot_word(event=None):
    update_word(current_word[0], 1, current_word[6], current_word[7] + 1, current_word[8] + 1)
    show_word_screen()


def add_new_word(event=None):

    def add(event=None):
        insert_new_word(entry_word, entry_meaning, add_word_window)

    add_word_window = tk.Toplevel(root)
    add_word_window.title("Add New Word")


    label_meaning = tk.Label(add_word_window, text="English:", font=("Arial", 10))
    entry_meaning = tk.Entry(add_word_window, font=("Arial", 10), width=50)
    label_word = tk.Label(add_word_window, text="Chinese:", font=("Arial", 10))
    entry_word = tk.Entry(add_word_window, font=("Arial", 10), width=50)
    add_button = tk.Button(add_word_window, text="Add",
                           command=lambda: insert_new_word(entry_word, entry_meaning, add_word_window)
                           , width=8, height=1)
    label_meaning.grid(row=1, column=1, padx=5, pady=1)
    entry_meaning.grid(row=1, column=2, padx=5, pady=1)
    label_word.grid(row=2, column=1, padx=5, pady=1)
    entry_word.grid(row=2, column=2, padx=5, pady=1)
    add_button.grid(row=3, column=2, padx=5, pady=1)

    add_word_window.bind("<Shift-Return>", add)


def insert_new_word(entry_word, entry_meaning, add_word_window):
    new_word = entry_word.get()
    new_meaning = entry_meaning.get()
    if new_word and new_meaning:
        insert_word(new_word, new_meaning)
        entry_word.delete(0, tk.END)
        entry_meaning.delete(0, tk.END)
        # add_word_window.destroy()


def show_meaning_screen(event=None):
    main_frame.pack_forget()
    show_frame.pack()
    root.unbind("<Down>")
    root.bind("<Left>", forgot_word)
    root.bind("<Right>", next_word)
    show_word_show()


def show_word_screen():
    show_frame.pack_forget()
    main_screen()


def view_all_words(event=None):
    all_words_window = tk.Toplevel(root)
    all_words_window.title("All Words")
    all_words_window.geometry('900x500')

    search_frame = tk.Frame(all_words_window)
    search_frame.pack(pady=10)

    search_label = tk.Label(search_frame, text="Search Word:")
    search_label.grid(row=0, column=0)

    search_entry = tk.Entry(search_frame)
    search_entry.grid(row=0, column=1)

    search_button = tk.Button(search_frame, text="Search", command=lambda: perform_search(search_entry.get()))
    search_button.grid(row=0, column=2)

    canvas = tk.Canvas(all_words_window)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(all_words_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    content_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=content_frame, anchor=tk.NW)

    def delete_word(id):
        try:
            cursor.execute("DELETE FROM words WHERE id = ?", (id,))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error when delete word: {str(e)}")
        try:
            perform_search(search_entry.get())
        except:
            perform_search("")

    def perform_search(keyword):
        # 清空现有内容
        for widget in content_frame.winfo_children():
            widget.destroy()

        cursor.execute('SELECT id, word, meaning, right, wrong, last_reviewed, next_review, interval FROM words WHERE word LIKE ? OR meaning LIKE ?', ('%' + keyword + '%', '%' + keyword + '%'))
        search_results = cursor.fetchall()

        if search_results:
            label_text = "{:^80} {:^90} {:^10} {:^5} {:^10} {:^10} {:^10}".format('English', 'Chinese', 'Rate', 'Option', 'Last Review', 'Next Review', 'Interval')
            label = tk.Label(content_frame, text=label_text, font=("Arial", 10))
            label.grid(row=0, column=0, columnspan=5)

            for idx, item in enumerate(search_results):
                id, word, meaning, right, wrong, last_review, next_review, interval = item
                error_rate = (wrong / (right + wrong)) if (right + wrong) != 0 else 0

                label_id = tk.Label(content_frame, text=f"{idx+1:^5}", font=("Arial", 10), anchor="w", justify="left")
                label_word = tk.Label(content_frame, text=f"{word:^60}", font=("Arial", 10), anchor="w", justify="left")
                label_meaning = tk.Label(content_frame, text=f"{meaning:^60}", font=("Arial", 10), anchor="w",
                                         justify="left")
                label_error_rate = tk.Label(content_frame, text=f"{error_rate:.2%}", font=("Arial", 10), anchor="w",
                                            justify="left")
                delete_button = tk.Button(content_frame, text="Delete", command=lambda id=id: delete_word(id))
                label_last_review = tk.Label(content_frame, text=f"{last_review:^10}", font=("Arial", 10), anchor="w",
                                            justify="left")
                label_next_review = tk.Label(content_frame, text=f"{next_review:^10}", font=("Arial", 10), anchor="w",
                                            justify="left")
                label_interval = tk.Label(content_frame, text=f"{interval:^10}", font=("Arial", 10), anchor="w",
                                            justify="left")

                label_id.grid(row=idx + 1, column=0)
                label_word.grid(row=idx + 1, column=1)
                label_meaning.grid(row=idx + 1, column=2)
                label_error_rate.grid(row=idx + 1, column=3)
                delete_button.grid(row=idx + 1, column=4, padx=20)
                label_last_review.grid(row=idx + 1, column=5)
                label_next_review.grid(row=idx + 1, column=6)
                label_interval.grid(row=idx + 1, column=7)

        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    perform_search("")


def main_screen():
    main_frame.pack()
    root.bind("<Down>", show_meaning_screen)
    root.unbind("<Left>")
    root.unbind("<Right>")
    show_word_main()
    # show_button.pack()
    # add_word_button.pack()
    # view_all_words_button.pack()  # 新增的按钮

# create main window
root = tk.Tk()
root.title("Word Reciting")
root.geometry('330x120')

main_frame = tk.Frame(root)
show_frame = tk.Frame(root)
add_word_window = None

word_label_main = tk.Label(main_frame, text="", font=("Arial", 8), width=40, height=2)
word_label = tk.Label(show_frame, text="", font=("Arial", 8), width=40, height=2)
meaning_label_main = tk.Label(main_frame, text="", font=("Arial", 1), width=40, height=2)
meaning_label = tk.Label(show_frame, text="", font=("Arial", 8), width=40, height=2)
show_button = tk.Button(main_frame, text="Translate", font=("Arial", 6), command=show_meaning_screen)
next_button = tk.Button(show_frame, text="Next", font=("Arial", 6), command=next_word)
forgot_button = tk.Button(show_frame, text="Forget", font=("Arial", 6), command=forgot_word)
add_word_button = tk.Button(main_frame, text="Add", font=("Arial", 6), command=add_new_word)
view_all_words_button = tk.Button(main_frame, text="View", font=("Arial", 6), command=view_all_words)
analysis = tk.Label(main_frame, text="", font=("Arial", 10))

entry_word = tk.Entry(add_word_window, font=("Arial", 10))
entry_meaning = tk.Entry(add_word_window, font=("Arial", 10))

main_screen()
root.mainloop()
