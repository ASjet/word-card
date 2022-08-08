const input = document.querySelector("#context");
const holder = document.querySelector("#words");

function RecordWord(event) {
  const word = Trim(event.target.textContent);
  card = JSON.stringify({
    "word": word,
    "context": input.value
  });
  fetch("/word", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: card
  }).then(response => response.json())
    .then(data => {
      const msg = document.createElement("p");
      msg.textContent = data.msg;
      holder.appendChild(msg);
    }).catch(err => {
      const msg = document.createElement("p");
      msg.textContent = `Failed to request！${err}`;
      msg.style.color = "#FF0000";
      holder.appendChild(msg);
    });
  input.value = "";
  holder.innerHTML = "";
}

function GenWord(content) {
  let word_block = document.createElement("code");
  word_block.setAttribute("class", "word");
  word_block.textContent = content
  return word_block;
}

function AddEvent() {
  const words = document.querySelectorAll(".word");
  for (let word of words) {
    word.onclick = RecordWord;
  }
}

function Trim(str) {
  str = str.replaceAll(/[^A-Za-z]/ig, '');
  return str;
}

function GetWordList() {
  const raw = input.value;
  let context = "";
  for (let word of raw.split(' ')) {
    if(word.length == 0) {
      continue;
    }
    if(context.length == 0) {
      context += word;
    } else {
      if(context[context.length-1] == '-') {
        context = context.slice(0, -1) + word;
      } else {
        context += ' ' + word;
      }
    }
  }
  holder.innerHTML = "";
  for (let word of context.split(' ')) {
    holder.appendChild(GenWord(word));
    holder.innerHTML += ' ';
  }
  input.value = context;
  AddEvent();
}

async function GetClipboard() {
  const text = await navigator.clipboard.readText();
  input.value = text;
}

function clear() {
  holder.innerHTML = "";
  input.value = "";
}

input.addEventListener("input", GetWordList);
document.querySelector("#clear").addEventListener("click", clear);

