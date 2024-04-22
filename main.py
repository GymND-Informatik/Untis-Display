from bs4 import BeautifulSoup
from datetime import datetime, date


def is_room(text):
  pass


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
    if element.get_text().isspace():
      continue
    # we are only interested in the table rows, they have all the info
    if element.name == 'tr':
      for child in element.contents:
        text = child.get_text().strip("\n").strip()
        if text == "Text":  #information begins
          mode = True
          continue
        if mode:
          if " " in text and "-" not in text:  # this means that we are reading a new class, since all classes have a space in them but there are hours with a dash so we filter those out
            if current_class:
              tokens.append(current_class)
            current_class = [text]
            continue
          current_class.append(text)
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

  return new_tokens, message


def write_new_html(tokens, message):
  file = open("template.html", 'r')
  soup = BeautifulSoup(file.read(), 'html.parser')
  table = soup.new_tag("table", id="scroll-table")

  thead = soup.new_tag("thead")
  new_row = soup.new_tag('tr', class_='list')
  for i in range(10):
    th_tag = soup.new_tag('th')
    th_tag.string = str(i) if i != 0 else ' '
    new_row.append(th_tag)

  thead.append(new_row)
  table.append(thead)

  soup.find("p").string = soup.find("p").get_text() + message

  tbody = soup.new_tag("tbody")
  for key, value in tokens.items():
    new_row = soup.new_tag('tr', class_='list')

    th_tag = soup.new_tag('th')
    th_tag.string = key
    new_row.append(th_tag)

    #extract what hours are targeted
    new_value = []
    #copy the array
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
      for i in range(11):
        if "-" in time:
          length = int(time[4]) - int(time[0]) + 1
          if i in range(int(time[0]), int(time[0]) + length):
            hours.append(i - 1)
        elif i == int(time):
          hours.append(i - 1)
      # no tenth hour
      hours = [x for x in hours if x != 10]
      # events that are 0 long and that are too long are discarded
      if len(hours) == 0 or len(hours) >= 9:
        new_value[n][0] = "[]"
        continue
      new_value[n][0] = str(hours).strip("[").strip("]")
      n += 1

    # keep track of how many supple hours, will be needed to decide if display at all
    supp_counter = []
    value = new_value
    print(value)
    for i in range(9):
      td_tag = soup.new_tag('td')
      td_tag.attrs["class"] = "leer"
      td_tag.string = " "
      for x in value:
        if str(i) in x[0]:
          if x[3] == "---":
            x2 = x[2].split("?")
            subject = x2[0]
            if (len(x2) > 1):
              subject = x2[1]
            td_tag.string = x[1] + " " + x[2] + " " + "AUSFALL"
            td_tag.attrs["class"] = "ausfall"
          else:
            td_tag.attrs["class"] = "supplieren"
            supp_counter.append(i)

            div = soup.new_tag('div')
            x1 = x[1].split("?")
            if (len(x1) > 1):
              p_tag = soup.new_tag("p", attrs={"class": "old"})
              p_tag.append(soup.new_tag("s"))
              p_tag.s.string = x1[0]
              td_tag.append(p_tag)
              p_tag2 = soup.new_tag("p", attrs={"class": "new"})
              p_tag2.string = x1[1]
              div.append(p_tag2)
            else:
              p_tag = soup.new_tag("p", attrs={"class": "new"})
              p_tag.string = x1[0]
              div.append(p_tag)
            td_tag.append(div)

            div = soup.new_tag('div')
            x2 = x[2].split("?")
            if (len(x2) > 1):
              p_tag = soup.new_tag("p", attrs={"class": "old"})
              p_tag.append(soup.new_tag("s"))
              p_tag.s.string = x2[0]
              td_tag.append(p_tag)
              p_tag2 = soup.new_tag("p", attrs={"class": "new"})
              p_tag2.string = x2[1]
              div.append(p_tag2)
            else:
              p_tag = soup.new_tag("p", attrs={"class": "new"})
              p_tag.string = x2[0]
              div.append(p_tag)
            td_tag.append(div)

            div = soup.new_tag('div')
            x3 = x[3].split("?")
            if (len(x3) > 1):
              p_tag = soup.new_tag("p", attrs={"class": "old"})
              p_tag.append(soup.new_tag("s"))
              p_tag.s.string = x3[0]
              td_tag.append(p_tag)
              p_tag2 = soup.new_tag("p", attrs={"class": "new"})
              p_tag2.string = x3[1]
              div.append(p_tag2)
            else:
              p_tag = soup.new_tag("p", attrs={"class": "new"})
              p_tag.string = x3[0]
              div.append(p_tag)
            td_tag.append(div)
            

      new_row.append(td_tag)
      if len(supp_counter):
        tbody.append(new_row)

    table.append(tbody)

  soup.find("div").append(table)
  return soup.prettify()


num = 1
tokens = {}
message = ""
# tokens, message = parse_html("subst_002.htm")
while True:
  try:
    filename = "subst_" + str(num).zfill(3) + ".htm"
    tokens_, msg = parse_html(filename)
    print("parsing", filename)
    if msg != "":
      message = msg
    for a, b in tokens_.items():
      tokens[a] = b

    num += 1
  except FileNotFoundError:
    break

# print(tokens, message)
new_html = write_new_html(tokens, message)
with open("new.html", "w") as file:
  file.write(new_html)
