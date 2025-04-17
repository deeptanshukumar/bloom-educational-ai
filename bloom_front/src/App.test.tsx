import { render, screen } from '@testing-library/react';
import App from './App';

test('renders Bloon sidebar', () => {
  render(<App />);
  const headingElement = screen.getByText(/Bloon/i);
  expect(headingElement).toBeInTheDocument();
});