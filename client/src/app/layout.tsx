import type { Metadata } from "next";
import { Roboto } from "next/font/google";
import "@/scss/globals.scss";

const roboto = Roboto({
  weight: ['100', '300', '400', '500', '700', '900'
  ],
});



export const metadata: Metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${roboto.className} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
