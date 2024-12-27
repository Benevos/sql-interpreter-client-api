import React from 'react'

function page() 
{
  return (
    <div>
        <h1>Formulario de contacto</h1>
        <form>
            <label>Nombre:</label>
            <input placeholder='Escribe tu nombre'/>

            <label>Mensaje:</label>
            <textarea className='Escribe tu mensaje aqui'></textarea>

            <button>Enviar</button>
        </form>
    </div>
  )
}

export default page