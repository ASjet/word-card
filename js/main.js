function RecordWord(event) {
  let word = Trim(event.target.textContent);
  card = JSON.stringify({
    "word": word,
    "sentence": sentence
  });
  console.log(card);
  alert(card);
}

function GenWord(content) {
  let word_block = document.createElement("code");
  word_block.setAttribute("class", "word");
  word_block.textContent = content
  return word_block;
}

function AddEvent() {
  let words = document.querySelectorAll(".word");
  for(let word of words) {
    word.onclick = RecordWord;
  }
}

function Trim(str) {
  str = str.replace(',', '');
  str = str.replace('.', '');
  str = str.replace('-', '');
  return str;
}

function GetWordList() {
  sentence = document.querySelector("#sentence").value;
  let holder = document.querySelector("#words");
  holder.innerHTML = "";
  for(let word of sentence.split(' ')) {
    holder.appendChild(GenWord(word));
    holder.innerHTML += " ";
  }
  AddEvent();
}

let sentence = "";
let button = document.querySelector("#btn");
button.onclick = GetWordList;
