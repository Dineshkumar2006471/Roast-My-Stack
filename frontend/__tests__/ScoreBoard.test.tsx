import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import ScoreBoard from '@/components/ScoreBoard'

const mockScores = {
  codeQuality: 83,
  security: 90,
  efficiency: 80,
  testing: 45,
  accessibility: 60,
}

describe('ScoreBoard Component', () => {
  it('renders all 5 score categories', () => {
    // We add overall to match user's expected test code, though the actual scoreboard recalculates overall internally if needed
    render(<ScoreBoard scores={mockScores} />)
    expect(screen.getByText(/code quality/i)).toBeInTheDocument()
    expect(screen.getByText(/security/i)).toBeInTheDocument()
    expect(screen.getByText(/efficiency/i)).toBeInTheDocument()
    expect(screen.getByText(/testing/i)).toBeInTheDocument()
    expect(screen.getByText(/accessibility/i)).toBeInTheDocument()
  })

  it('displays the overall score', () => {
    render(<ScoreBoard scores={mockScores} />)
    // 83+90+80+45+60 = 358 / 5 = 71.6 -> 72
    expect(screen.getByText('72')).toBeInTheDocument()
  })

  it('renders progress bars for each category', () => {
    render(<ScoreBoard scores={mockScores} />)
    const progressBars = screen.getAllByRole('progressbar')
    expect(progressBars.length).toBeGreaterThanOrEqual(5)
  })

  it('applies correct ARIA values to progress bars', () => {
    render(<ScoreBoard scores={mockScores} />)
    const bars = screen.getAllByRole('progressbar')
    bars.forEach(bar => {
      expect(bar).toHaveAttribute('aria-valuenow')
      expect(bar).toHaveAttribute('aria-valuemin', '0')
      expect(bar).toHaveAttribute('aria-valuemax', '100')
    })
  })
})
