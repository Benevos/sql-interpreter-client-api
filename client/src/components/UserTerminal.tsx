/* eslint-disable @typescript-eslint/no-unused-vars */

'use client';

import { ReactTerminal } from "react-terminal";
import React, { useState } from 'react'
import { v4 as uuid } from "uuid";


interface TokenType {
    type: string,
    value: string
}

interface QueryType {
    success: boolean,
    message: string
    tokens: TokenType[]
}

function UserTerminal() 
{
    const [continueCommand, setContinueCommand] = useState<boolean>(false)
    const [commnadContinuation, setCommnadContinuation] = useState<string[]>([])

    const welcomeMessage = (
        <span>Escriba el comando {'"'}<strong>help</strong>{'"'} para obtener ayuda sobre los comandos disponibles<br/></span>
    )

    const commands = {
        help: (commandArguments: string) =>
        {
            return (
                <span>
                    SQL: <br/>
                    - <strong>SELECT</strong>: Selecciona elementos de una tabla <br/>
                    - <strong>INSERT</strong>: Inserta elementos en una tabla <br/>
                    - <strong>UPDATE</strong>: Actualiza elementos en una tabla <br/>
                    - <strong>DELETE</strong>: Elimina elementos en una tabla
                </span>
            )
        }
    }

    const queryHandler = async (command: string, commandArguments: string) =>
    { 
        console.log(command, commandArguments)

        const response = await fetch("http://localhost:8085/query", {
            method: "POST",
            body: JSON.stringify({
                content: `${command} ${commandArguments}`
            }),
            headers: {
                'Content-Type': 'application/json; charset=UTF-8'
            }
        })

        setContinueCommand(false)
        setCommnadContinuation([]);

        const data: QueryType = await response.json()

        console.log(data.tokens)

        if(!data.success)
        {
            return <span>{data.message}</span>
        }

        const splittedMessage = data.message.split("\n");

        return (
            <span>{
                splittedMessage.map((slice, index, arr) => 
                {
                    if(index + 1 === arr.length)
                    {
                        return <React.Fragment key={uuid()}>{slice}</React.Fragment>
                    }
                    
                    return <React.Fragment key={uuid()}>{slice} <br/> </React.Fragment>
                })
            }</span>
        )
    }

    const defaultHandler = (command: string, commandArguments: string) =>
    {
        const clearedCommand = command.trim().toLowerCase();

        if( clearedCommand === "select" ||
            clearedCommand === "delete" ||
            clearedCommand === "update" ||
            clearedCommand === "insert" ||
            clearedCommand === 'show')
        {

            if(!commandArguments.trim().endsWith(";"))
            {
                setContinueCommand(true)
                const newContinuation = [...commnadContinuation]
                newContinuation.push(`${command} ${commandArguments}`);
                setCommnadContinuation(newContinuation)

                return "";
            }

            return queryHandler(command, commandArguments)
        }

        if(continueCommand)
        {
            const newContinuation = [...commnadContinuation]
            console.log(newContinuation)

            if(clearedCommand.endsWith(";"))
            {
                return queryHandler(commnadContinuation.join(" "), command);
            }
            else if(commandArguments.trim().endsWith(";"))
            {
                return queryHandler(commnadContinuation.join(" "), `${command} ${commandArguments}`);
            }

            newContinuation.push(`${command} ${commandArguments}`);
            setCommnadContinuation(newContinuation)
            return "";
        }
            

        return `ERROR: El comando ${command} no es valido`
    }


    return (
        <div className="w-[95%] max-md:w-full h-[510px] max-h-[510px]">
            <ReactTerminal
                welcomeMessage={welcomeMessage}
                prompt={"BenevosSQL>"} 
                defaultHandler={defaultHandler}
                showControlButtons={false}
                commands={commands}
                theme={"material-ocean"}/>
        </div>
    )
}

export default UserTerminal