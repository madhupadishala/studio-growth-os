import type { Metadata, Viewport } from 'next'
import { Inter, Playfair_Display } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import { Toaster } from 'sonner'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'Studiox | Professional Photography in Hyderabad',
    template: '%s | Studiox Photography',
  },
  description: 'Studiox Photography - Expert wedding, maternity, birthday & baby shower photography in Hyderabad. 500+ events captured. Book your session today.',
  keywords: ['photography', 'wedding photography', 'maternity photography', 'birthday photography', 'baby shower photography', 'Hyderabad', 'Dilsukhnagar'],
  authors: [{ name: 'Studiox Photography' }],
  creator: 'Studiox Photography',
  publisher: 'Studiox Photography',
  robots: 'index, follow',
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: 'https://rungrow.in',
    siteName: 'Studiox Photography',
    title: 'Studiox | Professional Photography in Hyderabad',
    description: 'Studiox Photography - Expert wedding, maternity, birthday & baby shower photography in Hyderabad. 500+ events captured.',
    images: [
      {
        url: 'https://images.unsplash.com/photo-1519741497674-611481863552?w=1200&h=630&fit=crop',
        width: 1200,
        height: 630,
        alt: 'Studiox Photography',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Studiox | Professional Photography in Hyderabad',
    description: 'Studiox Photography - Expert wedding, maternity, birthday & baby shower photography in Hyderabad.',
    images: ['https://images.unsplash.com/photo-1519741497674-611481863552?w=1200&h=630&fit=crop'],
    creator: '@studioxphotograpghy',
  },
  verification: {
    google: 'google-site-verification-code',
  },
}

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#1a1a2e' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://images.unsplash.com" />
        <link rel="dns-prefetch" href="https://images.unsplash.com" />
      </head>
      <body className={`${inter.variable} ${playfair.variable} font-sans antialiased`}>
        <Providers>
          {children}
          <Toaster position="top-right" />
        </Providers>
      </body>
    </html>
  )
}