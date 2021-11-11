#Author ludusnetfree@gmail.com 
#coded on 25 oct 2021 at 6AM  v 1.0.0
# https://github.com/acidutzu

books = int(input('how many books?')) #number of books
book_pages = int(input('how many pages on a book?')) #number of pages on one book
total_pages = books*book_pages
book_page_words = int(input('how many words on a page?')) # number of words/page
reading_time_perpage = float(input('how many minutes read time for one page?')) # time in minutes required to read one page
hours_read_time_per_day = int(input('how many reading hours a day?'))
hours_a_day = 24
year_days = 365
hours_a_year = year_days*hours_a_day



reading_time_perbook = (reading_time_perpage*book_pages)/60 #in hours
reading_time_perword = (reading_time_perpage/book_page_words)*60 #reading in seconds per word
reading_time_perword_minutes = (reading_time_perpage/book_page_words)

total_reading_hours = (total_pages*reading_time_perpage)/60 #total reading time in hours


total_reading_years_time = total_reading_hours/(hours_read_time_per_day*year_days)

print('You will finish:' ,books, 'books in:' ,total_reading_years_time,
'years with a total of:',total_reading_hours,
'hours by reading one book in',reading_time_perbook,
'hours every day for',hours_read_time_per_day,' hours with a speed of: ',reading_time_perword,
'seconds/word and a total of:',total_pages,'pages')