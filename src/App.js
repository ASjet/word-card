import "./App.css";
import Tab from "./Tabs";

function App() {
  return (
    <div className="App">
      <h1 id="title">Word Card</h1>
      <div
        style={{
          width: "100%",
        }}
      >
        <Tab></Tab>
      </div>
    </div>
  );
}

export default App;
