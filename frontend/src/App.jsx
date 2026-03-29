import React from 'react'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Garmin Workout Creator
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Phase 1: Project Setup Complete ✅
          </p>
          <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
            <h2 className="text-2xl font-semibold mb-4">Next Steps</h2>
            <ul className="text-left space-y-2 text-gray-700">
              <li>• Phase 2: Backend API development</li>
              <li>• Phase 3: Frontend components</li>
              <li>• Phase 4: Security hardening</li>
              <li>• Phase 5: Testing and deployment</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
