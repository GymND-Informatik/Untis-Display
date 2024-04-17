from bs4 import BeautifulSoup
special_rooms = ["MUSIK", "BIOL"]

def parse_html(filename):
  with open(filename, 'r', encoding="iso-8859-1") as file:
    html_content = file.read()

  soup = BeautifulSoup(html_content, 'html.parser')

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
  
  mode = False
  current_class = None
  tokens = []  
  
  for element in soup.find_all():
    if element.get_text().isspace():
      continue
    if element.name == 'tr':
      for child in element.contents:
        # print("type: '", element.name, "' - content: '", child.get_text().strip("\n").strip(), "'")
        text = child.get_text().strip("\n").strip()
        
        if (text == "Text"): #information begins
          mode = True
          continue
        if mode:
          if " " in text and "-" not in text:
            if current_class:
              tokens.append(current_class)
            current_class = [text]
            continue 
          current_class.append(text)
  tokens.append(current_class)

  # print(tokens, mode)
  new_tokens = {}
  for token in tokens:
    el = []
    li = []
    for i in range(1, len(token)):
      li.append(token[i])
      if i % 5 == 0:
        li.pop()
        el.append(li)
        li = []
    new_tokens[token[0]] = el
    
  return new_tokens, message

def write_new_html(tokens, message):
  file = open("template.html", 'r')
  soup = BeautifulSoup(file.read(), 'html.parser')
  body = soup.find("body")
  body.append(soup.new_tag("table"))
  
  new_row = soup.new_tag('tr', class_='list')
  for i in range(11):
    th_tag = soup.new_tag('th')
    th_tag.string = str(i) if i != 0 else ' '
    new_row.append(th_tag)
  soup.find("table").append(new_row)

  soup.find("p").string = soup.find("p").get_text() + message
  
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
      new_value[n][0] = str(hours).strip("[").strip("]")
      n += 1
      
    value = new_value

    for i in range(10):
      th_tag = soup.new_tag('td')
      th_tag.attrs["class"] = "leer"
      th_tag.string = " "
      for x in value:
        if str(i) in x[0]:
          if x[3] == "---":
            x2 = x[2].split("?")
            subject = x2[0]
            if (len(x2) > 1):
              subject = x2[1]
            th_tag.string = subject + " " + "AUSFALL"
            th_tag.attrs["class"] = "ausfall"
          else:
            text = ""
            x1 = x[1].split("?")
            teacher = x1[0]
            if (len(x1) > 1):
              teacher = x1[1]
              text += teacher + " "
            x2 = x[2].split("?")
            subject = x2[0]
            if (len(x2) > 1):
              subject = x2[1]
              text += subject + " "
            x3 = x[3].split("?")
            room = x3[0]
            if (len(x3) > 1):
              room = x3[1]
              text += room

            th_tag.attrs["class"] = "supplieren"
            th_tag.string = text
      new_row.append(th_tag)
    
    soup.find("table").append(new_row)
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

print(tokens, message)
new_html = write_new_html(tokens, message)
with open("new.html", "w") as file:
  file.write(new_html)
