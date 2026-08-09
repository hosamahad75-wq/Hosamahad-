import React from 'react'
import PaymentsPanel from './components/payments/PaymentsPanel'

function App() {
  return (
    <div className="min-h-screen bg-[radial-gradient(ellipse at_top_left,_#071122,_#02040A)] text-white p-6">
      <div className="max-w-4xl mx-auto">
        <PaymentsPanel />
      </div>
    </div>
  )
}

export default App
