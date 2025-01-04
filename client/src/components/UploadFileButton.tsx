'use client';

import React, { useRef } from 'react'
import { FaFileUpload } from 'react-icons/fa'

function UploadFileButton() 
{
    const fileIputRef = useRef<HTMLInputElement>(null);

    const handleSubmit = (e: React.FormEvent) =>
    {
        e.preventDefault()

        const fileInput = fileIputRef.current;
        fileInput!.click();
    }

    const handleFileChange = async ({ currentTarget: { files } }: React.ChangeEvent<HTMLInputElement>) => 
    {
        if (!files) 
        {
            alert("ERROR: Se requiere un archivo");
            return;
        }

        if (files.length !== 1) 
        {
            alert("ERROR: Se requiere exactamente un archivo");
            return;
        }

        const file = files[0];

        if (!file.name.endsWith(".csv")) 
        {
            alert("ERROR: El archivo debe tener formato CSV");
            return;
        }

        const alias = prompt("Escribe el nombre del alias para la tabla:");
        if (!alias || alias.trim() === "") 
        {
            alert("ERROR: Se necesita un alias para la tabla");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("table_alias", alias);

        try 
        {
            const response = await fetch("http://localhost:8085/upload", 
            {
                method: "POST",
                body: formData,
            });

            if (!response.ok) 
            {
                const errorData = await response.json();
                alert(`ERROR: ${errorData.message}`);
                return;
            }

            const data = await response.json();

            alert(`Archivo subido exitosamente:\n- Nombre: ${data.filename}\n- Alias: ${data.alias}`);
        } 
        catch (error) 
        {
            console.error("Error al subir el archivo:", error);
            alert("ERROR: No se pudo subir el archivo. Revisa la consola para más detalles.");
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input ref={fileIputRef} onChange={handleFileChange} type='file' name='upload' className='hidden'/>
            <button className="w-[70px] h-[70px] text-5xl bg-slate-600 rounded-md flex flex-col items-center justify-center
                            hover:bg-slate-500 active:bg-slate-400 transition-all ">
                <FaFileUpload color='white'/>
            </button>
        </form>
    )
}

export default UploadFileButton