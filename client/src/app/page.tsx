'use client';
import Header from "@/components/Header";
import UploadFileButton from "@/components/UploadFileButton";
import UserTerminal from "@/components/UserTerminal";
import { TerminalContextProvider } from "react-terminal";

export default function Home() 
{
  

  return (
    <TerminalContextProvider>
      <div className="bg-slate-900 h-full w-full flex justify-center">
        <div className="h-full max-w-[1480px] w-full bg-slate-800 flex flex-col items-center">

          <div className="w-full flex items-center justify-center text-white text-4xl py-4 font-bold animate-pulse">
            <div className="relative ">
            BenevosSQL
              <div className="absolute text-base top-8 -right-8">
                by Kevin Mendoza
              </div>
            </div>
          </div>

          <div className="w-full py-6 flex flex-col items-center">
            <UploadFileButton/>
            <label className="text-white tracking-widest">Subir CSV</label>
          </div>

          <UserTerminal/>
          
        </div>
      </div>
    </TerminalContextProvider>
  );
}
