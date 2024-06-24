from bs4 import BeautifulSoup, NavigableString
from datetime import datetime, date

program_directory = ""
wpflf = open(program_directory + "wpflf.txt", "r").read().split("\n")
uu = open(program_directory + "uu.txt", "r").read().split("\n")
ignore = open(program_directory + "ignore.txt", "r").read().split("\n")
source_path = "/mnt/storage/external/"
output_path = "/var/www/Untis/"

def is_class(text):
  if len(text) <= 1:
    return False
  if text[0].isnumeric() and text[1].isalpha():
    return True
  if text.find("Matura") != -1: # matura
    return True
  if text[:2] == "FS": # fremdschule
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

  # date 
  table_mon_title = soup.find('div', class_='mon_title')
  date_text = table_mon_title.get_text().split(" ")[0]
  if datetime.strptime(date_text, "%d.%m.%Y").date() != date.today():
    print("Date is not today, skipping tokens.")
    return None, None

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
        if type(child) == NavigableString:
          continue
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

def format_text(soup, x, extra=False):
  div = soup.new_tag('div')
  div.attrs["class"] = "supplieren-item"
  if extra:
    div.attrs["class"] = "extra-item"
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
  new_list = {}
  for key, value in list.items():
    for v in value:
      val = [v[2], v[1], v[0]]
      key_new = val[0]+" "+val[1]
      if key_new not in new_list:
        new_list[key_new] = val
        new_list[key_new].append(key)
      else:
        new_list[key_new].append(key)
  list = new_list
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
      div = soup.new_tag('div')
      div.attrs["class"] = "extra-container"
      div2 = soup.new_tag('div')
      div2.attrs["class"] = "extra-item"
      div2.string = key.split(" ")[0] + " (Stunde " + (simplify_range(item[2]) if "," in item[2] else item[2]) + ")"
      div.append(div2)
      for x in item:
        print(x)
        div.append(format_text(soup, x, extra=True))
      td_tag.append(div)
    new_row.append(td_tag)
    return new_row

def write_new_html(tokens, message):
  # open the html template and find the table
  file = open(program_directory + "template.html", 'r')
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

  if not message:
    message = "------"
  # enter the daily message up top
  soup.find("p", class_="message").string = str(soup.find("p", class_="message").get_text()) + " " + str(message)

  if len(tokens) == 0:
    soup.find("p", class_="message").string = str(soup.find("p", class_="message").get_text()) + " | Keine Supplierungen gefunden."

  # create the table body
  tbody = soup.new_tag("tbody")

  # create the special subjects lists
  wpflf_list = {}
  uu_list = {}

  for key, value in tokens.items():
    # ignore fs
    if key[0] == "F" and key[1] == "S":
      continue

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
          # ignore some things
          if any(y in ignore for y in x) or key in ignore:
            continue
          # means the hour is in the array of hours that are suppld
          if str(i + 1) in x[0]:
            # check for special subjects
            subject = x[2].split("?")[0] if len(x[2].split("?")) > 1 else x[2]
            if subject in wpflf:
              if key in wpflf_list:
                if x not in wpflf_list[key]:
                  wpflf_list[key].append(x)
              else:
                wpflf_list[key] = [x]
              continue
            elif subject in uu:
              if key in uu_list:
                if x not in uu_list[key]:
                  uu_list[key].append(x)
              else:
                uu_list[key] = [x]
              continue

            supp_counter.append(i)

            # means the hour completely drops, give it its own class and handle accordingly
            if x[3] == "---":
              div = soup.new_tag('div')
              div.attrs["class"] = "ausfall-div"
              for k in range(3):
                td_tag.attrs["class"] = "ausfall"
                s_tag = soup.new_tag("s", attrs={"class": "old"})
                s_tag.string = x[k]
                div.append(s_tag)
              td_tag.append(div)

            # otherwise we have suppl, mark with class and append the information
            else:
              td_tag.attrs["class"] = "supplieren"
              # append new divs to the table data, each for every information, teacher, class, room
              div = soup.new_tag('div')
              div.attrs["class"] = "supplieren-container"
              div.append(format_text(soup, x[1]))
              div.append(format_text(soup, x[2]))
              div.append(format_text(soup, x[3]))
              td_tag.append(div)

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

  # wpflf extras
  wpflf_supp = display_extra(soup, wpflf_list, "WLPFF")
  if wpflf_supp:
    tbody.append(wpflf_supp)

  # uu extras
  print(uu_list)
  uu_supp = display_extra(soup, uu_list, "UÜ")
  if uu_supp:
    tbody.append(uu_supp)

  # append the whole table body to the table and the table to the div
  table.append(tbody)
  soup.find("div", class_="main-div").append(table)

  # print(wpflf_list, uu_list)
  return soup.prettify()

num = 1
tokens = {}
message = ""
# tokens, message = parse_html("subst_002.htm")
while True:
  filename = source_path + "subst_" + str(num).zfill(3) + ".htm"
  # print("parsing", filename)
  try:
    tokens_, msg = parse_html(filename)
    if msg != "":
      message = msg
    if tokens_:
      for a, b in tokens_.items():
        tokens[a] = b
    num += 1
  except Exception as e:
    error_message = f"Error Occurred: {str(e)}"
    print("Error parsing file", filename, "|", error_message)
    break

# print(tokens, message)
# print(wpflf, uu)

new_html = write_new_html(tokens, message)
with open(output_path + "index.html", "w") as file:
  file.write(new_html)
