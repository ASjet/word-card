import * as React from 'react';
import Box from '@mui/material/Box';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert from '@mui/material/Alert';

import { FixedSizeList } from 'react-window';
import { retriveWords, retriveDefine, masterWord, deleteWord } from './api';

const Alert = React.forwardRef(function Alert(props, ref) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" severity={props.severity}>{props.message}</MuiAlert>;
});

class WordCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      words: [],
      word: "",
      mastered: false,
      contexts: [],
      defines: [],
      open: false,
      msgType: "success",
      msg: "",
      vertical: 'top',
      horizontal: 'center',
    };
  }

  componentDidMount() {
    this.getWordList();
  }

  clear = () => {
    this.setState({ open: false });
  }

  getWordList = () => {
    retriveWords()
      .then(res => {
        this.setState({
          words: res.data
        });
        // Default render first word's definition
        if(res.data && res.data.length > 0) {
          this.getDefine(res.data[0]);
        }
      });
  }

  getDefine = (word) => {
    retriveDefine(word)
      .then(res => {
        if (res.success) {
          const data = res.data;
          let defs = [];
          for (const cate in data.definitions) {
            defs.push({
              category: cate,
              senses: data.definitions[cate]
            })
          }
          this.setState({
            word: data.word,
            mastered: data.mastered,
            contexts: data.context,
            defines: defs
          });
        } else {
          this.setState({
            open: true,
            msgType: "error",
            msg: res.msg
          });
        }
      });
  }

  renderDefine = (event) => {
    const word = event.target.innerText;
    this.getDefine(word);
  }

  renderWordList = (props) => {
    const { index, style, data } = props;
    const word = data[index];
    return (
      <ListItem style={style} key={index} component="div" disablePadding>
        <ListItemButton onClick={this.renderDefine}>
          <ListItemText primary={word} />
        </ListItemButton>
      </ListItem>
    );
  }

  markAsMastered = (event) => {
    masterWord(this.state.word)
      .then((res) => {
        this.setState({
          open: true,
          msgType: res.success ? "success" : "error",
          msg: res.msg
        });
      });
  }

  delete = (event) => {
    deleteWord(this.state.word)
      .then((res) => {
        this.setState({
          open: true,
          msgType: res.success ? "success" : "error",
          msg: res.msg
        });
        this.getWordList();
      });
  }

  render = () => {
    return (
      <div
        style={{
          height: "600px",
          margin: "10px",
          display: "flex",
          flexDirection: "row",
        }}
      >
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
        <Box
          sx={{ width: '100%', height: 400, maxWidth: 360, bgcolor: 'background.paper' }}
        >
          <FixedSizeList
            height={600}
            width={200}
            itemSize={46}
            itemData={this.state.words}
            itemCount={this.state.words.length}
            overscanCount={5}
          >
            {this.renderWordList}
          </FixedSizeList>
        </Box>
        <div
          style={{
            height: "600px",
            width: "60%",
            justifyContent: "center",
          }}
        >
          <Card sx={{ minWidth: 275 }}>
            <CardContent>
              <Typography variant="h5" component="div">
                {this.state.word}
              </Typography>
              <Typography sx={{ fontSize: 14 }} color="text.secondary" gutterBottom component="div">
                {this.state.contexts.map(c => (<p key={c}>{c}</p>))}
              </Typography>
              {this.state.defines.map(d => (
                <div key={d.category}>
                  <Typography sx={{ mb: 1.5 }} color="text.secondary">
                    {d.category}
                  </Typography>
                  <Typography variant="body2">
                    {d.senses.map(s => (<p key={s}>{s}</p>))}
                  </Typography>
                </div>
              ))}
            </CardContent>
            <CardActions>
              <Button size="small" onClick={this.markAsMastered}>Mark as mastered</Button>
              <Button size="small" onClick={this.delete}>Delete</Button>
            </CardActions>
          </Card>

        </div>

      </div>
    );
  }
}

export default WordCard;
