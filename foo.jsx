const Component = ()=> {
  const [text, setText] = useState(textState);

  const onChange = (event) => {
    setText(event.target.value);
  };

  return (
    <div>
      <TextInput text={text} setText={setText} />
    </div>
  )
}

function TextInput({ text, setText}) {

  return (
    <React.Fragment >
      <input type="text" value={text} onChange={setText('HOLLA')} />
      <br />
      Echo: {text}

    </React.Fragment>
   
  );
}
