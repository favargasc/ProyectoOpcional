import React, { useState } from 'react'

const useFooState = () => {
  const [foo, setFoo] = useState(); // no enviar el set

  const handleChange = (e) => setFoo(e.target.value)

  return {
    foo,
    handleChange // la idea es no delegar la funcionalidad a otro componente
  }
}

const Foo = ({text, setText}) => { // utiliza el estado de la app principal de
  return (
    <>
      <input value={text} onChange={setText} />
    </>
  )
}

export default function App() {
  const {foo, handleChange } = useFooState() // utiliza el estado desacoplado

  return (
    <div className="App">
     <input type="text" value={foo} onChange={handleChange} />
     <h1>{foo}</h1>
     <Foo text={foo} setText={handleChange}/>
    </div>
  );
}
