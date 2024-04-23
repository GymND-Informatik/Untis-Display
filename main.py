from bs4 import BeautifulSoup
from datetime import datetime, date

wpflf = open("wpflf.txt", "r").read().split("\n")
uu = open("uu.txt", "r").read().split("\n")
reli = open("reli.txt", "r").read().split("\n")


def is_class(text):
  if len(text) <= 1:
    return False
  if text[0].isnumeric() and text[1].isalpha():
    return True
  else:
    return False


def rearrange_values(value):
  new_value = []
  for v in value:
    li = []
    for w in v:
      li.append(w)
    new_value.append(li)

  n = 0
  for x in value:
    time = x[0]
    length = 1
    hours = []
    for i in range(10):
      if "-" in time:
        length = int(time[4]) - int(time[0]) + 1
        if i in range(int(time[0]), int(time[0]) + length):
          hours.append(i)
      elif i == int(time):
        hours.append(i)
    # no tenth hour
    hours = [x for x in hours if x != 10]
    # events that are 0 long and that are too long are discarded (set to no duration)
    if len(hours) == 0 or len(hours) >= 9:
      new_value[n][0] = "[]"
      continue
    new_value[n][0] = str(hours).strip("[").strip("]")
    n += 1

  return new_value


def parse_html(filename):
  with open(filename, 'r', encoding="iso-8859-1") as file:
    html_content = file.read()

  soup = BeautifulSoup(html_content, 'html.parser')

  # date (don't care for now)
  table_mon_title = soup.find('div', class_='mon_title')
  date_text = table_mon_title.get_text().split(" ")[0]
  if (datetime.strptime(date_text, "%d.%m.%Y").date() != date.today()):
    print("Date is not today, skipping tokens.")
    # return

  # message of the day
  table_info = soup.find('table', class_='info')
  message = ""
  if table_info:
    tr_elements = table_info.find_all('tr')
    if (len(tr_elements) > 2):
      last_tr = tr_elements[2]
      message += last_tr.text.strip()
    else:
      message += "------"

  # parsing tokens
  mode = False
  current_class = None
  tokens = []

  for element in soup.find_all():
    # we are only interested in the table rows, they have all the info
    if element.name == 'tr':
      for child in element.contents:
        text = child.get_text().strip("\n").strip()
        if text == "Text":  #information begins
          mode = True
        elif mode:
          if is_class(text):  # information about a new class starts flowing in
            if current_class:
              tokens.append(
                  current_class
              )  # append every time for a new class all the information collected about it
            current_class = [text]
            continue
          current_class.append(text)

  # append one last time
  tokens.append(current_class)

  # rearrange the tokens once again into a dictionary
  new_tokens = {}
  for token in tokens:
    el = []
    li = []
    for i in range(1, len(token)):
      li.append(token[i])
      if i % 5 == 0:
        # pop the special text, we don't need it
        li.pop()
        # append the rest of the info
        el.append(li)
        li = []
    new_tokens[token[0]] = el

  # edit the hours into an array instead of the original range e.g. "1-2" -> ["1", "2"]
  for key, value in new_tokens.items():
    new_tokens[key] = rearrange_values(value)

  return new_tokens, message

def format_text(soup, x):
  div = soup.new_tag('div')
  x1 = x.split("?")
  if (len(x1) > 1):
    s_tag = soup.new_tag('s', attrs={"class": "old"})
    s_tag.string = x1[0]
    div.append(s_tag)
    p_tag = soup.new_tag("p", attrs={"class": "new"})
    p_tag.string = x1[1]
    div.append(p_tag)
  else:
    p_tag = soup.new_tag("p", attrs={"class": "new"})
    p_tag.string = x1[0]
    div.append(p_tag)
  return div

def simplify_range(input_string):
  input_string = input_string.strip("[").strip("]")
  # Split the input string by comma and strip any whitespace
  numbers = [int(num.strip()) for num in input_string.split(",")]

  # Get the minimum and maximum numbers
  min_num = min(numbers)
  max_num = max(numbers)

  # Return the simplified range string
  return f"{min_num} - {max_num}"

def display_extra(soup, list, name):
  # rearrange extras
  if len(list):
    new_row = soup.new_tag('tr')
    new_row.attrs["class"] = "extra"
    th_tag = soup.new_tag('th')
    th_tag.string = name
    new_row.append(th_tag)
    td_tag = soup.new_tag('td')
    td_tag.attrs["class"] = "leer"
    td_tag.attrs["colspan"] = 9
    for key, item in list.items():
      for x in item:
        div = soup.new_tag('div')
        div2 = soup.new_tag('div')
        div2.string = key + " (" + (simplify_range(x[0]) if "," in x[0] else x[0]) + ")"
        div.append(div2)
        div.append(format_text(soup, x[1]))
        div.append(format_text(soup, x[2]))
        div.append(format_text(soup, x[3]))
        td_tag.append(div)
      
    new_row.append(td_tag)
    return new_row
  

def write_new_html(tokens, message):
  # error handling
  if len(tokens) == 0:
    error_message = "<div><h1>Error Occurred in the parsing. Lmao bad luck.</h1><p>Go talk to Herr Proffesor Kaintz.</p><p>Yours truly, Jacques.</p></div>"
    soup = BeautifulSoup(error_message, 'html.parser')
    return soup.prettify()

  # open the html template and find the table
  file = open("template.html", 'r')
  soup = BeautifulSoup(file.read(), 'html.parser')
  table = soup.new_tag("table", id="scroll-table")

  # create the table header that will always display the hours 1 through 9
  thead = soup.new_tag("thead")
  new_row = soup.new_tag('tr')
  for i in range(10):
    th_tag = soup.new_tag('th')
    th_tag.string = str(i) if i != 0 else ''
    new_row.append(th_tag)
  thead.append(new_row)
  table.append(thead)

  # enter the daily message up top
  soup.find("p").string = soup.find("p").get_text() + message

  # create the table body
  tbody = soup.new_tag("tbody")

  # create the special subjects lists
  wpflf_list = {}
  uu_list = {}
  reli_list = {}

  for key, value in tokens.items():
    # create a new row and add a header to it, the class name
    new_row = soup.new_tag('tr')
    th_tag = soup.new_tag('th')
    th_tag.string = key
    new_row.append(th_tag)

    # keep track of how many suppl hours, will be needed to decide if display at all
    supp_counter = []

    # loop through all hours and write the information into table data cells
    for i in range(9):
      try:
        # create a new data cell and give it empty text and the "leer" class
        td_tag = soup.new_tag('td')
        td_tag.attrs["class"] = "leer"
        td_tag.string = ""

        # check every suppl hour whether it fits into the current hour
        for x in value:  
          # means the hour is in the array of hours that are suppld
          if str(i + 1) in x[0]:
            # check for special subjects
            subject = x[2].split("?")[0] if len(x[2].split("?")) > 1 else x[2]
            if subject in wpflf:
              if key in wpflf_list:
                if not x in wpflf_list[key]:
                  wpflf_list[key].append(x)
              else:
                wpflf_list[key] = [x]
              continue
            elif subject in uu:
              if key in uu_list:
                if not x in uu_list[key]:
                  uu_list[key].append(x)
              else:
                uu_list[key] = [x]
              continue
            elif subject in reli:
              if key in reli_list:
                if not x in reli_list[key]:
                  reli_list[key].append(x)
              else:
                reli_list[key] = [x]
              continue
            
            supp_counter.append(i)

            # means the hour completely drops, give it its own class and handle accordingly
            if x[3] == "---":
              div = soup.new_tag('div')
              for k in range(3):
                td_tag.attrs["class"] = "ausfall"
                s_tag = soup.new_tag("s", attrs={"class": "old"})
                s_tag.string = x[2 - k]
                div.append(s_tag)
              td_tag.append(div)

            # otherwise we have suppl, mark with class and append the information
            else:
              td_tag.attrs["class"] = "supplieren"
              # append new divs to the table data, each for every information, teacher, class, room
              td_tag.append(format_text(soup, x[1]))
              td_tag.append(format_text(soup, x[2]))
              td_tag.append(format_text(soup, x[3]))

        # append the table data from above to the row
        new_row.append(td_tag)

      except Exception as e:
        # handle an error by replacing information with "ERROR"
        td_tag = soup.new_tag('td')
        td_tag.attrs["class"] = "error"
        td_tag.string = "ERROR"
        print("Error handling hour", i, "for class", key, "with error:", e)
        new_row.append(td_tag)

      # if there aren't any suppl hours at all, skip
      if len(supp_counter):
        tbody.append(new_row)
  
  # reli extras
  reli_supp = display_extra(soup, reli_list, "RELI")
  if reli_supp:
    tbody.append(reli_supp)

  # wpflf extras
  wpflf_supp = display_extra(soup, wpflf_list, "WLPFF")
  if wpflf_supp:
    tbody.append(wpflf_supp)

  # uu extras
  uu_supp = display_extra(soup, uu_list, "UÜ")
  if uu_supp:
    tbody.append(uu_supp)

  # append the whole table body to the table and the table to the div
  table.append(tbody)
  soup.find("div").append(table)
  
  print(wpflf_list, uu_list, reli_list)
  return soup.prettify()

num = 1
tokens = {}
message = ""
# tokens, message = parse_html("subst_002.htm")
while True:
  filename = "subst_" + str(num).zfill(3) + ".htm"
  print("parsing", filename)
  try:
    tokens_, msg = parse_html(filename)
    if msg != "":
      message = msg
    for a, b in tokens_.items():
      tokens[a] = b
    num += 1
  except Exception as e:
    error_message = f"Error Occurred: {str(e)}"
    print("Error parsing file", filename, "|", error_message)
    break

print(tokens, message)
print(wpflf, uu, reli)
new_html = write_new_html(tokens, message)
with open("new.html", "w") as file:
  file.write(new_html)
