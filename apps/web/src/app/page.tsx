import Link from 'next/link'
import { ArrowRight, Camera, Heart, Award, Calendar, MapPin, Phone, Mail, MessageSquare, Youtube, Instagram, ChevronRight } from 'lucide-react'

const occasions = [
  { slug: 'birthday', name: 'Birthday', price: '₹9,999', duration: '3 hrs', icon: Heart, description: 'Candid moments, cake cutting, fun portraits' },
  { slug: 'maternity', name: 'Maternity', price: '₹7,999', duration: '2 hrs', icon: Heart, description: 'Artistic portraits, couple shots, milk bath' },
  { slug: 'baby-shower', name: 'Baby Shower', price: '₹11,999', duration: '4 hrs', icon: Camera, description: 'Candid + posed, decor, family moments' },
  { slug: 'marriage', name: 'Marriage', price: '₹21,999', duration: '6 hrs', icon: Award, description: '150 photos, 5-min film, teaser, drone' },
  { slug: 'full-marriage', name: 'Full Marriage', price: '₹1,25,000', duration: '2 days', icon: Award, description: '400 photos, 15-min film, 4 albums, drone included' },
]

const trustIndicators = [
  { label: '500+ Events', icon: Calendar },
  { label: '7+ Years', icon: Award },
  { label: '100% Satisfaction', icon: Heart },
]

const serviceAreas = ['Dilsukhnagar', 'LB Nagar', 'Kothapet', 'Malakpet', 'Nagole', 'Chaithanyapuri', 'Saroor Nagar']

export default function HomePage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=1920&q=80"
            alt="Studiox Photography"
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black/60" />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <span className="inline-block px-4 py-2 rounded-full bg-white/10 backdrop-blur-sm text-white text-sm font-medium mb-6">
              Serving Hyderabad & Surrounding Areas
            </span>
            <h1 className="font-heading text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 text-balance">
              Capturing Moments,{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-red-500">
                Creating Memories
              </span>
            </h1>
            <p className="text-xl sm:text-2xl text-white/90 max-w-3xl mx-auto mb-10 font-light leading-relaxed">
              Professional photography for every occasion in Hyderabad.
              Weddings, maternity, birthdays, baby showers — we capture it all.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/contact"
                className="group inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-pink-500 to-red-600 rounded-full hover:from-pink-600 hover:to-red-700 transition-all duration-300 shadow-lg shadow-pink-500/25"
              >
                Plan Your Shoot
                <ArrowRight className="ml-2 w-5 h-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                href="/services"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-white border-2 border-white/30 rounded-full hover:bg-white/10 backdrop-blur-sm transition-all duration-300"
              >
                View Packages
              </Link>
            </div>
          </div>

          {/* Trust Indicators */}
          <div className="mt-20 grid grid-cols-3 gap-8 max-w-4xl mx-auto">
            {trustIndicators.map((item, index) => (
              <div key={index} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-white/10 backdrop-blur-sm mb-4">
                  <item.icon className="w-8 h-8 text-white" />
                </div>
                <p className="text-2xl font-bold text-white">{item.label.split(' ')[0]}+</p>
                <p className="text-white/70 text-sm">{item.label.split(' ').slice(1).join(' ')}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <svg className="w-6 h-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>
      </section>

      {/* Occasions/Packages */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="font-heading text-4xl font-bold text-gray-900 mb-4">
              Photography for Every Occasion
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              From intimate maternity sessions to grand wedding celebrations,
              we have a package tailored for your special moments.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {occasions.map((occasion) => (
              <article
                key={occasion.slug}
                className="group relative overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm hover:shadow-xl transition-all duration-500"
              >
                <div className="relative aspect-[4/3] overflow-hidden">
                  <img
                    src={`https://images.unsplash.com/photo-${occasion.slug === 'full-marriage' ? '1519741497674-611481863552' : occasion.slug === 'marriage' ? '1537633264530-89cbd31b0b65' : occasion.slug === 'baby-shower' ? '1519183071298-a2962be91b0e' : occasion.slug === 'maternity' ? '1595899411377-591ce2e0b77f' : '1530103862676-de8c9debad1d'}?w=800&q=80`}
                    alt={`${occasion.name} photography by Studiox`}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                  <div className="absolute bottom-4 left-4 right-4 text-white">
                    <span className="inline-block px-3 py-1 text-sm font-medium bg-white/10 backdrop-blur-sm rounded-full">
                      {occasion.duration}
                    </span>
                  </div>
                </div>
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <occasion.icon className="w-5 h-5 text-pink-500" />
                    <h3 className="font-heading text-xl font-bold text-gray-900">{occasion.name}</h3>
                  </div>
                  <p className="text-gray-600 mb-4">{occasion.description}</p>
                  <div className="flex items-baseline justify-between">
                    <span className="font-heading text-2xl font-bold text-gray-900">{occasion.price}</span>
                    <Link
                      href={`/services/${occasion.slug}`}
                      className="inline-flex items-center gap-1 text-sm font-medium text-pink-600 hover:text-pink-700"
                    >
                      View Details
                      <ChevronRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link
              href="/services"
              className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold text-pink-600 border-2 border-pink-200 rounded-full hover:bg-pink-50 transition-colors"
            >
              View All Packages
              <ChevronRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Service Areas */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="font-heading text-4xl font-bold text-gray-900 mb-4">
              Serving Hyderabad & Beyond
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Based in Dilsukhnagar, we cover all major Hyderabad localities
              with free travel within city limits.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-3">
            {serviceAreas.map((area) => (
              <span
                key={area}
                className="px-4 py-2 bg-white text-gray-700 rounded-full border border-gray-200 hover:border-pink-300 hover:text-pink-600 transition-colors"
              >
                {area}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-pink-600 to-red-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="font-heading text-4xl font-bold text-white mb-6">
            Ready to Book Your Session?
            <br />
            <span className="text-pink-200">Let's Create Something Beautiful Together</span>
          </h2>
          <p className="text-xl text-pink-100 mb-10 max-w-2xl mx-auto">
            Fill out our quick form or message us on WhatsApp. Our AI assistant
            will guide you through packages, check availability, and send a quote
            within hours.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/contact"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-semibold text-pink-600 bg-white rounded-full hover:bg-gray-100 transition-colors shadow-lg"
            >
              Get Your Quote
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <a
              href="https://wa.me/917285988958"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-4 text-lg font-semibold text-white border-2 border-white/30 rounded-full hover:bg-white/10 backdrop-blur-sm transition-colors"
            >
              <MessageSquare className="w-5 h-5" />
              Chat on WhatsApp
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            <div className="md:col-span-2">
              <h3 className="font-heading text-2xl font-bold mb-4">Studiox Photography</h3>
              <p className="text-gray-400 mb-6 max-w-md">
                Capturing life's most precious moments with authenticity and artistry.
                Professional photography for weddings, maternity, birthdays, and baby showers
                in Hyderabad and surrounding areas.
              </p>
              <div className="flex gap-6">
                <a href="https://instagram.com/studioxphotograpghy" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                  <Instagram className="w-6 h-6" />
                </a>
                <a href="https://youtube.com/@mandatisreenath" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                  <Youtube className="w-6 h-6" />
                </a>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Contact</h4>
              <address className="not-italic text-gray-400 space-y-2">
                <p><MapPin className="inline w-4 h-4 mr-2" /> Dilsukhnagar, Hyderabad, Telangana 500060</p>
                <p><Phone className="inline w-4 h-4 mr-2" /> <a href="tel:+917285988958" className="hover:text-white transition-colors">+91 72859 88958</a></p>
                <p><Mail className="inline w-4 h-4 mr-2" /> <a href="mailto:support@rungrow.in" className="hover:text-white transition-colors">support@rungrow.in</a></p>
              </address>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Quick Links</h4>
              <nav className="space-y-2">
                <Link href="/services" className="block text-gray-400 hover:text-white transition-colors">Packages</Link>
                <Link href="/about" className="block text-gray-400 hover:text-white transition-colors">About Us</Link>
                <Link href="/contact" className="block text-gray-400 hover:text-white transition-colors">Book Now</Link>
                <Link href="/privacy" className="block text-gray-400 hover:text-white transition-colors">Privacy Policy</Link>
              </nav>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; {new Date().getFullYear()} Studiox Photography. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  )
}