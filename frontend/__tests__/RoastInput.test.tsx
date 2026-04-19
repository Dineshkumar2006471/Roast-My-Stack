import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'

import RoastInput from '@/components/RoastInput'

describe('RoastInput Component', () => {
  const mockOnSubmit = jest.fn()

  describe('Initial render', () => {
    it('renders the GitHub URL tab by default', () => {
      render(<RoastInput onSubmit={mockOnSubmit} isLoading={false} />)
      expect(screen.getByRole('tab', { name: /github url/i })).toBeInTheDocument()
    })

    it('renders the Paste Code tab', () => {
      render(<RoastInput onSubmit={mockOnSubmit} isLoading={false} />)
      expect(screen.getByRole('tab', { name: /paste code/i })).toBeInTheDocument()
    })

    it('submit button is disabled when input is empty', () => {
      render(<RoastInput onSubmit={mockOnSubmit} isLoading={false} />)
      const button = screen.getByRole('button', { name: /Submit code for AI review/i })
      expect(button).toBeDisabled()
    })

    it('has Senior Review selected by default', () => {
      render(<RoastInput onSubmit={mockOnSubmit} isLoading={false} />)
      const seniorRadio = screen.getByRole('radio', { name: /Senior Review/i })
      expect(seniorRadio).toBeChecked()
    })
  })

  describe('Input validation', () => {
    it('enables submit button when GitHub URL is entered', async () => {
      render(<RoastInput onSubmit={mockOnSubmit} isLoading={false} />)
      const input = screen.getByPlaceholderText(/github.com/i)
      await userEvent.type(input, 'https://github.com/user/repo')
      const button = screen.getByRole('button', { name: /Submit code for AI review/i })
      expect(button).not.toBeDisabled()
    })
  })

  describe('Accessibility', () => {
    it('intensity options are in a radio group', () => {
      render(<RoastInput onSubmit={mockOnSubmit} isLoading={false} />)
      const radios = screen.getAllByRole('radio')
      expect(radios.length).toBe(3)
    })
  })
})
