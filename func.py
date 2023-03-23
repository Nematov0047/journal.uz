import sqlite3

def generate_page(page_number):
    start_page = (page_number*1)+((page_number-1)*5)
    end_page = page_number*5
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT *,rowid FROM diaries WHERE rowid BETWEEN "+str(start_page)+" AND "+str(end_page))
    results = c.fetchall()
    conn.commit()
    conn.close()

    for result in results:
        print(result)

def generate_paging(page_number = 1):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM diaries")
    results = c.fetchall()
    page = (int(results[0][0]/5))+1
    conn.commit()
    conn.close()
    print(page)
    output = ''
    if page_number == 1:
        output += '<li class="page-item disabled"><a class="page-link" href="#">Previous</a></li>'
    else:
        output += '<li class="page-item"><a class="page-link" href="#">Previous</a></li>'
    index = 1
    while index <= page:
        output += '<li class="page-item"><a class="page-link" href="#">'+str(index)+'</a></li>'
        index += 1
    if page_number == page:
        output += '<li class="page-item disabled"><a class="page-link" href="#">Next</a></li>'
    else:
        output += '<li class="page-item"><a class="page-link" href="#">Next</a></li>'
    return output

print(generate_paging())