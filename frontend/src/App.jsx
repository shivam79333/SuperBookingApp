import { useState } from 'react'
import './App.css'
import Hero from './pages/Hero'
import Gallery from './pages/Gallery'
import TicketCard from './pages/TicketCard'
import Reviews from './pages/Reviews'
import FAQ from './pages/FAQ'

function App() {
  return (
    <>
      <Hero/>
      <Gallery/>
      <TicketCard title="MoMA Entry Ticket" price="30"/>
      <TicketCard title="MoMA + Edge Combo" price="60"/>
      <Reviews/>
      <FAQ/>
    </>
  )
}

export default App
