import csv
import os
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Progressbar, Combobox
from Trie import Trie
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt / 10)




required_dir = None
files_list = []
index_dict = {}
myTrie = Trie()
main_root = Tk()
main_root.title('INVERTED INDEX')


def Choose_Dir():
    global required_dir, main_root
    main_root.withdraw()
    required_dir = filedialog.askdirectory(parent=main_root, initialdir="/", title='Please select a directory')
    Load_Data()


def Load_Data():
    global files_list, required_dir, index_dict, myTrie
    index_dict.clear()
    myTrie = Trie()
    files_list = os.listdir(required_dir)
    files_list.sort()

    def Load_Dict():
        with open(str(required_dir) + '/build_data/index.csv', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                myTrie.add_word(row['word'],*list(row['Doc_ID'].split('/')))
                #index_dict[row['word']] = list(row['Doc_ID'].split('/'))

    def Save_Dict():
        try:
            os.mkdir(str(required_dir) + '/build_data')
            os.remove(str(required_dir) + '/build_data/index.csv')
            os.remove(str(required_dir) + '/build_data/files_list.txt')
        except:
            pass

        with open(str(required_dir) + '/build_data/index.csv', 'w', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['word', 'Doc_ID'])
            writer.writeheader()
            for key, value in index_dict.items():
                writer.writerow({'word': key, 'Doc_ID': '/'.join(value)})
        with open(str(required_dir) + '/build_data/files_list.txt', 'w', encoding="utf-8") as file:
            file.writelines('\n'.join(files_list))

    def Make_Dict():
        def Progress_Update(prog):
            prog = round(int(prog) / len(files_list) * 100, 1)
            load_bar.config(value=prog)
            prog_label.config(text=str(prog) + '%')
            load_root.update()

        load_root = Tk()
        load_root.title('LOADING')

        load_label = Label(load_root, text='\tLoading... \t\n')
        load_label.grid(row=0, columnspan=2, padx=30, pady=10)

        load_bar = Progressbar(load_root, orient=HORIZONTAL, length=200, mode='determinate')
        load_bar.grid(row=1, padx=10, pady=20, sticky=E)
        prog_label = Label(load_root, text='00%')
        prog_label.grid(row=1, column=1, sticky=W, padx=10)

        counter = int(0)
        for file_name in files_list:
            with open(str(required_dir) + '/' + str(file_name), encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                tmp_list = list(set(re.findall("['\w]+", line.lower())))
                for word in tmp_list:
                    myTrie.add_word(word, str(file_name))
                    if word in index_dict:
                        index_dict[word].append(str(file_name))
                    else:
                        index_dict[word] = [str(file_name)]

            counter += 1
            Progress_Update(counter)

        Save_Dict()
        load_root.destroy()
        print(myTrie.Trie_Root.edge.keys())
        print('done')

    if 'build_data' in files_list:
        files_list.pop(files_list.index('build_data'))
        index_path = str(required_dir) + '/build_data/index.csv'
        files_list_path = str(required_dir) + '/build_data/files_list.txt'
        if os.path.exists(index_path) and os.stat(index_path).st_size > 0 and os.path.exists(
                files_list_path) and os.stat(files_list_path).st_size > 0:
            with open(files_list_path, encoding="utf-8") as f:
                check_list = f.read().split()
            if check_list == files_list:
                Load_Dict()
            else:
                Make_Dict()
        else:
            Make_Dict()
    else:
        Make_Dict()

    Search_Windows()


def Search_Windows():
    search_root = Tk()
    search_root.title('FIND')

    def Show_Result():
        search_root.withdraw()
        result_root = Tk()
        result_root.title('RESULT')

        def Show_File(event):
            output_text.config(state="normal")
            output_text.delete(1.0, END)
            output_text.tag_config("a", foreground="black", background="yellow", )

            with open(str(required_dir) + '/' + str(result_box.get()), encoding="utf-8") as f:
                file = f.read()
            splits = re.findall(f"[\W]*{'{1}'.join(query) + '{1}'}?[\W]+", file.lower())
            for sp in splits:
                tp = file.lower().find(sp) + sp.find(query)
                output_text.insert(INSERT, file[:tp])
                output_text.insert(INSERT, file[tp:tp + len(query)], "a")
                file = file[tp + len(query):]

            output_text.insert(INSERT, file)

            output_text.config(state="disabled")

        scrolly = Scrollbar(result_root)
        scrolly.grid(row=0, rowspan=5, sticky='ns')

        output_text = Text(result_root, yscrollcommand=scrolly.set)
        scrolly.config(command=output_text.yview)
        output_text.grid(row=0, rowspan=5, column=1, columnspan=2)

        result_label = Label(result_root, text='______Select File to View______\n. . . . .')
        result_label.grid(row=0, column=4, columnspan=2, padx=20, pady=10)

        result_box = Combobox(result_root, justify='center', value=[], state='readonly')
        result_box.bind("<<ComboboxSelected>>", Show_File)
        result_box.grid(row=1, column=4, columnspan=2, padx=20, pady=10)

        back_button = Button(result_root, text='Back', command=lambda: [result_root.destroy(), search_root.deiconify()])
        back_button.grid(row=4, column=4, columnspan=2, padx=5, pady=10)

        query = query_entry.get().lower()
        res = myTrie.get_doc(query)
        if res:
            result_box['value'] = res
            output_text.config(state="normal")
            output_text.delete(1.0, END)
            output_text.insert(END,
                               f'The number of documents having "{query_entry.get()}" = {len(res)}\n' + '\n'.join(res))

            output_text.config(state="disabled")
        else:
            output_text.config(state="normal")
            output_text.delete(1.0, END)
            output_text.insert(END,
                               f'The number of documents having "{query_entry.get()}" = "None"\n')
            output_text.config(state="disabled")

    query_label = Label(search_root, text='______Query Word______\n. . . . .')
    query_label.grid(row=0, columnspan=2, padx=30, pady=10)

    query_entry = Entry(search_root)
    query_entry.grid(row=1, columnspan=2, padx=30, pady=10)

    search_button = Button(search_root, text='Search', command=Show_Result)
    search_button.grid(row=1, column=2, sticky=W, padx=5, pady=10)

    update_button = Button(search_root, text='Update', command=lambda: [search_root.destroy(), os.remove(
        str(required_dir) + '/build_data/index.csv'), Load_Data()])
    update_button.grid(row=2, column=1, padx=5, pady=10)

    reload_button = Button(search_root, text='Reload', command=lambda: [search_root.destroy(), main_root.deiconify()])
    reload_button.grid(row=3, column=1, padx=5, pady=10)

    exit_button = Button(search_root, text='Exit', command=lambda: [search_root.destroy(), main_root.destroy()])
    exit_button.grid(row=4, column=1, padx=5, pady=10)


choose_label = Label(main_root, text='______Choose Required Directory______\n. . . . .')
choose_label.grid(row=0, columnspan=4, padx=30, pady=20)

choose_button = Button(main_root, text='Browse', command=Choose_Dir)
choose_button.grid(row=1, columnspan=4, padx=30, pady=10)

main_root.mainloop()
