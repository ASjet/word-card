import * as React from 'react';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" severity={props.severity}>{props.message}</MuiAlert>;
});

class Context extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      msgType: "success",
      msg: "",
      context: "",
      words: [],
      vertical: 'top',
      horizontal: 'center',
    };
  }
  clear = () => {
    this.setState({ open: false, msg: "", context: "", words: [] });
  }
  genWords = (context) => {
    const words = context.split(' ').filter((word) => {
      return word.length > 0;
    });
    this.setState({
      words: (words.map((word) => (
        <Chip
          key={word}
          label={word}
          onClick={this.recordWord}
          color="primary"
          variant="outlined"
          sx={{
            margin: "5px"
          }}
        />
      ))
      )
    })
  }
  getWordList = (event) => {
    const raw = event.target.value;
    let context = "";
    for (let word of raw.split(' ')) {
      if (word.length === 0) {
        continue;
      }
      if (context.length === 0) {
        context += word;
      } else {
        if (context[context.length - 1] === '-') {
          context = context.slice(0, -1) + word;
        } else {
          context += ' ' + word;
        }
      }
    }
    if (raw[raw.length - 1] === ' ') {
      context += ' ';
    }
    this.setState({ context: context });
    this.genWords(context);
  }
  recordWord = (event) => {
    const word = event.target.textContent.replaceAll(/[^A-Za-z]/ig, '');
    const record = JSON.stringify({
      "word": word,
      "context": this.state.context
    });
    console.log(record);
    this.setState({
      words: (<CircularProgress />)
    })
    fetch("/word", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: record
    }).then(response => response.json())
      .then(data => {
        this.setState({
          open: true,
          msgType: "success",
          msg: data.msg
        });
      }).catch(err => {
        this.setState({
          open: true,
          msgType: "error",
          msg: "Record failed"
        });
      });
    this.clear();
  }
  render = () => {
    return (
      <div>
        <Snackbar
          open={this.state.open}
          autoHideDuration={1000}
          onClose={this.clear}
          anchorOrigin={{
            vertical: this.state.vertical,
            horizontal: this.state.horizontal
          }}
        >
          <Alert severity={this.state.msgType} sx={{ width: '100%' }} message={this.state.msg} />
        </Snackbar>
        <div
          style={{
            margin: "10px",
            display: "flex",
            flexDirection: "row",
            justifyContent: "center",
          }}
        >
          <TextField
            id="context"
            label="Context"
            type="text"
            variant="outlined"
            value={this.state.context}
            onChange={this.getWordList}
            sx={{
              leftMargin: "10px",
              rightMargin: "10px",
              width: "80%"
            }}
          />
          <IconButton
            id="clear"
            onClick={this.clear}
            size="large"
            sx={{
            }}
          >
            <DeleteIcon />
          </IconButton>
        </div>
        <div id="words">
          {this.state.words}
        </div>
      </div>
    );
  }
}

export default Context;
