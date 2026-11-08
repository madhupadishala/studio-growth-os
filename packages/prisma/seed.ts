// ============================================================================
// Studio Growth OS - Prisma Seed (Studiox Demo Data)
// ============================================================================

import { PrismaClient } from '@prisma/client'
import { hash } from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding Studiox demo data...')

  // ============================================================================
  // TENANT & BRAND
  // ============================================================================
  const tenant = await prisma.tenant.upsert({
    where: { id: 'studiox' },
    update: {},
    create: {
      id: 'studiox',
      slug: 'studiox',
      name: 'Studiox',
      status: 'active',
      planId: 'growth_automation',
      brandConfig: {
        logo_url: 'https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=200&h=200&fit=crop',
        primary_color: '#1a1a2e',
        secondary_color: '#e94560',
        font_heading: 'Playfair Display',
        font_body: 'Inter',
        hero_tagline: 'Capturing Moments, Creating Memories',
        hero_subtext: 'Professional photography for every occasion in Hyderabad',
        address: 'Dilsukhnagar, Hyderabad, Telangana 500060',
        phone: '+917285988958',
        email: 'support@rungrow.in',
        website: 'https://rungrow.in',
        instagram: 'https://instagram.com/studioxphotograpghy',
        youtube: 'https://youtube.com/@mandatisreenath',
        service_areas: ['Dilsukhnagar', 'LB Nagar', 'Kothapet', 'Malakpet', 'Nagole', 'Chaithanyapuri', 'Saroor Nagar'],
        owner_name: 'Madhu Padishala'
      }
    }
  })

  await prisma.tenantDomain.upsert({
    where: { hostname: 'rungrow.in' },
    update: {},
    create: {
      tenantId: 'studiox',
      hostname: 'rungrow.in',
      verificationStatus: 'verified',
      verifiedAt: new Date()
    }
  })

  await prisma.tenantDomain.upsert({
    where: { hostname: 'studiox.rungrow.in' },
    update: {},
    create: {
      tenantId: 'studiox',
      hostname: 'studiox.rungrow.in',
      verificationStatus: 'verified',
      verifiedAt: new Date()
    }
  })

  await prisma.planEntitlement.upsert({
    where: { planId_version: { planId: 'growth_automation', version: 1 } },
    update: {},
    create: {
      planId: 'growth_automation',
      version: 1,
      features: {
        website: true, crm: true, lead_engine: true, quote_booking: true,
        ai_agent: true, campaign_connectors: true, template_manager: true,
        intelligent_followups: true, automated_quotes: true, content_workflows: true,
        funnel_intelligence: true, pricing_negotiation: true, availability_slots: true,
        payment_reconciliation: true, contract_lifecycle: true, benchmarking: true,
        marketplace: true, predictive_scoring: true, anomaly_alerts: true
      },
      quotas: {
        monthly_leads: 500, monthly_quotes: 200, monthly_bookings: 100,
        monthly_whatsapp_messages: 1000, monthly_ai_conversations: 200,
        storage_gb: 10, team_members: 10, custom_domains: 2
      },
      effectiveFrom: new Date('2026-01-01')
    }
  })

  // ============================================================================
  // USERS & TEAM
  // ============================================================================
  const users = await Promise.all([
    prisma.user.upsert({
      where: { id: 'user_madhu' },
      update: {},
      create: { id: 'user_madhu', email: 'support@rungrow.in', name: 'Madhu Padishala', phoneE164: '+917285988958', avatarUrl: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face' }
    }),
    prisma.user.upsert({
      where: { id: 'user_ramu' },
      update: {},
      create: { id: 'user_ramu', email: 'ramu@studiox.in', name: 'Ramu', avatarUrl: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&crop=face' }
    }),
    prisma.user.upsert({
      where: { id: 'user_venkatesh' },
      update: {},
      create: { id: 'user_venkatesh', email: 'venkatesh@studiox.in', name: 'Venkatesh', avatarUrl: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face' }
    }),
    prisma.user.upsert({
      where: { id: 'user_adithya' },
      update: {},
      create: { id: 'user_adithya', email: 'adithya@studiox.in', name: 'Adithya', avatarUrl: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&h=200&fit=crop&crop=face' }
    }),
    prisma.user.upsert({
      where: { id: 'user_guru' },
      update: {},
      create: { id: 'user_guru', email: 'guru@studiox.in', name: 'Guru', avatarUrl: 'https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=200&h=200&fit=crop&crop=face' }
    }),
    prisma.user.upsert({
      where: { id: 'user_natony' },
      update: {},
      create: { id: 'user_natony', email: 'natony@studiox.in', name: 'Natony', avatarUrl: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop&crop=face' }
    }),
    prisma.user.upsert({
      where: { id: 'user_abdul' },
      update: {},
      create: { id: 'user_abdul', email: 'abdul@studiox.in', name: 'Abdul', avatarUrl: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=200&h=200&fit=crop&crop=face' }
    })
  ])

  const [userMadhu, userRamu, userVenkatesh, userAdithya, userGuru, userNatony, userAbdul] = users

  await Promise.all([
    prisma.membership.upsert({ where: { userId_tenantId: { userId: 'user_madhu', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_madhu', tenantId: 'studiox', role: 'studio.owner', status: 'active' } }),
    prisma.membership.upsert({ where: { userId_tenantId: { userId: 'user_ramu', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_ramu', tenantId: 'studiox', role: 'studio.manager', status: 'active' } }),
    prisma.membership.upsert({ where: { userId_tenantId: { userId: 'user_venkatesh', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_venkatesh', tenantId: 'studiox', role: 'studio.sales', status: 'active' } }),
    prisma.membership.upsert({ where: { userId_tenantId: { userId: 'user_adithya', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_adithya', tenantId: 'studiox', role: 'studio.sales', status: 'active' } }),
    prisma.membership.upsert({ where: { userId_tenantId: { userId: 'user_guru', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_guru', tenantId: 'studiox', role: 'studio.editor', status: 'active' } }),
    prisma.membership.upsert({ where: { userId_tenantId: { userId: 'user_natony', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_natony', tenantId: 'studiox', role: 'studio.editor', status: 'active' } }),
    prisma.membership.upsert({ where: { userId_tenantId: { userId: 'user_abdul', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_abdul', tenantId: 'studiox', role: 'studio.viewer', status: 'active' } })
  ])

  await Promise.all([
    prisma.teamProfile.upsert({ where: { userId_tenantId: { userId: 'user_ramu', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_ramu', tenantId: 'studiox', roleTitle: 'Lead Photographer', specialties: ['weddings', 'portraits', 'lighting_design'], hourlyRatePaise: 500000, isActive: true } }),
    prisma.teamProfile.upsert({ where: { userId_tenantId: { userId: 'user_venkatesh', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_venkatesh', tenantId: 'studiox', roleTitle: 'Videographer / Editor', specialties: ['cinematic_films', 'same_day_edits', 'color_grading'], hourlyRatePaise: 400000, isActive: true } }),
    prisma.teamProfile.upsert({ where: { userId_tenantId: { userId: 'user_adithya', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_adithya', tenantId: 'studiox', roleTitle: 'Associate Photographer', specialties: ['candid', 'events', 'drone'], hourlyRatePaise: 300000, isActive: true } }),
    prisma.teamProfile.upsert({ where: { userId_tenantId: { userId: 'user_guru', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_guru', tenantId: 'studiox', roleTitle: 'Assistant / Lighting Tech', specialties: ['equipment', 'off_camera_flash', 'studio_setup'], hourlyRatePaise: 200000, isActive: true } }),
    prisma.teamProfile.upsert({ where: { userId_tenantId: { userId: 'user_natony', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_natony', tenantId: 'studiox', roleTitle: 'Album Designer / Retoucher', specialties: ['album_layout', 'fine_art_retouch', 'color_correction'], hourlyRatePaise: 350000, isActive: true } }),
    prisma.teamProfile.upsert({ where: { userId_tenantId: { userId: 'user_abdul', tenantId: 'studiox' } }, update: {}, create: { userId: 'user_abdul', tenantId: 'studiox', roleTitle: 'Junior Photographer / Coordinator', specialties: ['client_coordination', 'bts_content', 'backup_shooter'], hourlyRatePaise: 150000, isActive: true } })
  ])

  // ============================================================================
  // PACKAGES & PRICING
  // ============================================================================
  const packages = await Promise.all([
    prisma.servicePackage.upsert({ where: { id: 'pkg_birthday' }, update: {}, create: { id: 'pkg_birthday', tenantId: 'studiox', name: 'Birthday Photoshoot', slug: 'birthday', description: '3-hour birthday photography session with edited photos and highlight reel', basePricePaise: 999900, currency: 'INR', durationHours: 3, deliverables: ['50 edited high-resolution photos', '2-minute cinematic highlight reel', 'Online gallery access (30 days)', 'USB drive with all deliverables'], addOns: [{ id: 'addon_drone', name: 'Drone Coverage', price_paise: 250000, description: 'Aerial shots of venue and surroundings' }, { id: 'addon_extra_hour', name: 'Extra Hour', price_paise: 200000, description: 'Additional hour of photography' }, { id: 'addon_same_day', name: 'Same-Day 50 Photos', price_paise: 300000, description: '50 edited photos delivered same day' }, { id: 'addon_album_8x8', name: 'Premium Album 8x8 (20pp)', price_paise: 450000, description: 'Hardcover photo album, 20 pages' }], travelPolicy: { free_km: 10, per_km_paise: 1500, parking_tolls_extra: true, studio_backup_available: false }, isActive: true, sortOrder: 1 } }),
    prisma.servicePackage.upsert({ where: { id: 'pkg_maternity' }, update: {}, create: { id: 'pkg_maternity', tenantId: 'studiox', name: 'Maternity Photoshoot', slug: 'maternity', description: '2-hour maternity photography session with artistic portraits', basePricePaise: 799900, currency: 'INR', durationHours: 2, deliverables: ['40 edited high-resolution photos', '1-minute cinematic maternity reel', 'Online gallery access (30 days)', 'USB drive with all deliverables'], addOns: [{ id: 'addon_drone', name: 'Drone Coverage', price_paise: 250000, description: 'Aerial shots of outdoor locations' }, { id: 'addon_extra_hour', name: 'Extra Hour', price_paise: 200000, description: 'Additional hour of photography' }, { id: 'addon_milk_bath', name: 'Milk Bath Setup', price_paise: 300000, description: 'Professional milk bath setup with props' }, { id: 'addon_album_8x8', name: 'Premium Album 8x8 (20pp)', price_paise: 450000, description: 'Hardcover photo album, 20 pages' }], travelPolicy: { free_km: 10, per_km_paise: 1500, parking_tolls_extra: true, studio_backup_available: true }, isActive: true, sortOrder: 2 } }),
    prisma.servicePackage.upsert({ where: { id: 'pkg_baby_shower' }, update: {}, create: { id: 'pkg_baby_shower', tenantId: 'studiox', name: 'Baby Shower Photoshoot', slug: 'baby-shower', description: '4-hour baby shower event photography with candid and posed shots', basePricePaise: 1199900, currency: 'INR', durationHours: 4, deliverables: ['75 edited high-resolution photos', '3-minute highlight reel', 'Online gallery access (30 days)', 'USB drive with all deliverables'], addOns: [{ id: 'addon_drone', name: 'Drone Coverage', price_paise: 250000, description: 'Aerial shots of venue' }, { id: 'addon_extra_hour', name: 'Extra Hour', price_paise: 200000, description: 'Additional hour of photography' }, { id: 'addon_album_10x10', name: 'Premium Album 10x10 (30pp)', price_paise: 600000, description: 'Large format hardcover album, 30 pages' }], travelPolicy: { free_km: 15, per_km_paise: 1500, parking_tolls_extra: true, decor_coordination: true }, isActive: true, sortOrder: 3 } }),
    prisma.servicePackage.upsert({ where: { id: 'pkg_marriage' }, update: {}, create: { id: 'pkg_marriage', tenantId: 'studiox', name: 'Marriage Photography', slug: 'marriage', description: '6-hour wedding day photography with cinematic film', basePricePaise: 2199900, currency: 'INR', durationHours: 6, deliverables: ['150 edited high-resolution photos', '5-minute cinematic wedding film', '1-minute teaser trailer', 'Online gallery access (60 days)', 'USB drive with all deliverables'], addOns: [{ id: 'addon_drone', name: 'Drone Coverage', price_paise: 300000, description: 'Aerial shots of venue and ceremony' }, { id: 'addon_extra_hour', name: 'Extra Hour', price_paise: 300000, description: 'Additional hour of photography/videography' }, { id: 'addon_second_shooter', name: 'Second Shooter', price_paise: 800000, description: 'Additional photographer for parallel coverage' }, { id: 'addon_same_day_edit', name: 'Same-Day Edit', price_paise: 600000, description: '3-minute highlight film delivered same day' }, { id: 'addon_premium_album', name: 'Premium Album 12x12 (40pp)', price_paise: 1200000, description: 'Large premium hardcover album, 40 pages' }], travelPolicy: { free_km: 15, per_km_paise: 2000, parking_tolls_extra: true, overnight_stay_if_over_50km: true }, isActive: true, sortOrder: 4 } }),
    prisma.servicePackage.upsert({ where: { id: 'pkg_full_marriage' }, update: {}, create: { id: 'pkg_full_marriage', tenantId: 'studiox', name: 'Full Marriage Coverage', slug: 'full-marriage', description: 'Complete 2-day wedding coverage with premium deliverables', basePricePaise: 12500000, currency: 'INR', durationHours: 16, deliverables: ['400 edited high-resolution photos', '15-minute cinematic wedding film', '1-minute teaser + 3-minute highlight', 'Online gallery access (90 days)', 'USB drive with all deliverables', '2x Premium Albums 12x12 (40pp each)', '2x Parent Albums 8x8 (20pp each)'], addOns: [{ id: 'addon_drone', name: 'Drone Coverage', price_paise: 0, description: 'Included in package' }, { id: 'addon_second_shooter', name: 'Second Shooter', price_paise: 0, description: 'Included in package' }, { id: 'addon_same_day_edit', name: 'Same-Day Edit', price_paise: 0, description: 'Included in package' }, { id: 'addon_pre_wedding', name: 'Pre-Wedding Shoot (2hr)', price_paise: 1500000, description: 'Separate pre-wedding session' }, { id: 'addon_extra_album', name: 'Extra Premium Album', price_paise: 800000, description: 'Additional 12x12 premium album' }], travelPolicy: { free_km: 25, per_km_paise: 2000, parking_tolls_extra: true, travel_stay_covered_if_over_50km: true }, isActive: true, sortOrder: 5 } })
  ])

  await prisma.pricingRule.upsert({
    where: { id: 'pricing_v1' },
    update: {},
    create: {
      id: 'pricing_v1', tenantId: 'studiox', version: 1, effectiveFrom: new Date('2026-01-01'),
      ruleJson: {
        margin_floor_pct: 25, discount_ceiling_pct: 15,
        approval_required_above_discount_pct: 10, approval_required_above_amount_paise: 5000000,
        seasonal_multipliers: { peak_season_months: [10, 11, 12, 1, 2], peak_multiplier: 1.15, off_season_months: [6, 7, 8], off_multiplier: 0.9 },
        travel_bands: [{ name: 'local', max_km: 25, per_km_paise: 2000, included_km: 15 }, { name: 'regional', max_km: 100, per_km_paise: 2500, included_km: 0 }, { name: 'outstation', max_km: 500, per_km_paise: 3000, included_km: 0 }],
        package_rules: { pkg_birthday: { min_price_paise: 799900, max_discount_pct: 15 }, pkg_maternity: { min_price_paise: 649900, max_discount_pct: 15 }, pkg_baby_shower: { min_price_paise: 959900, max_discount_pct: 15 }, pkg_marriage: { min_price_paise: 1759900, max_discount_pct: 10 }, pkg_full_marriage: { min_price_paise: 10000000, max_discount_pct: 10 } },
        add_on_rules: { drone: { requires_dgca_certified: true, max_discount_pct: 0 }, second_shooter: { requires_lead_approval: true, max_discount_pct: 10 }, same_day_edit: { max_discount_pct: 0 } },
        discount_codes: { EARLYBIRD10: { type: 'percentage', value: 10, valid_until: '2026-12-31', min_booking_value_paise: 2000000, stackable: false }, REFERRAL5: { type: 'percentage', value: 5, valid_until: '2026-12-31', min_booking_value_paise: 1000000, stackable: true }, WEEKDAY15: { type: 'percentage', value: 15, valid_until: '2026-12-31', min_booking_value_paise: 3000000, days: [1,2,3,4], stackable: false } }
      },
      currency: 'INR', approvedBy: 'user_madhu', isActive: true
    }
  })

  await prisma.pricingRule.upsert({
    where: { id: 'pricing_v2_draft' },
    update: {},
    create: {
      id: 'pricing_v2_draft', tenantId: 'studiox', version: 2, effectiveFrom: new Date('2026-07-01'),
      ruleJson: {
        margin_floor_pct: 30, discount_ceiling_pct: 12,
        approval_required_above_discount_pct: 8, approval_required_above_amount_paise: 4000000,
        seasonal_multipliers: { peak_season_months: [10, 11, 12, 1, 2, 3], peak_multiplier: 1.2, off_season_months: [6, 7, 8], off_multiplier: 0.85 },
        travel_bands: [{ name: 'local', max_km: 30, per_km_paise: 2200, included_km: 20 }, { name: 'regional', max_km: 100, per_km_paise: 2800, included_km: 0 }, { name: 'outstation', max_km: 500, per_km_paise: 3500, included_km: 0 }],
        package_rules: { pkg_birthday: { min_price_paise: 849900, max_discount_pct: 12 }, pkg_maternity: { min_price_paise: 699900, max_discount_pct: 12 }, pkg_baby_shower: { min_price_paise: 1019900, max_discount_pct: 12 }, pkg_marriage: { min_price_paise: 1859900, max_discount_pct: 8 }, pkg_full_marriage: { min_price_paise: 10500000, max_discount_pct: 8 } },
        add_on_rules: { drone: { requires_dgca_certified: true, max_discount_pct: 0 }, second_shooter: { requires_lead_approval: true, max_discount_pct: 8 }, same_day_edit: { max_discount_pct: 0 } },
        discount_codes: { EARLYBIRD10: { type: 'percentage', value: 10, valid_until: '2026-12-31', min_booking_value_paise: 2000000, stackable: false }, REFERRAL5: { type: 'percentage', value: 5, valid_until: '2026-12-31', min_booking_value_paise: 1000000, stackable: true }, WEEKDAY15: { type: 'percentage', value: 15, valid_until: '2026-12-31', min_booking_value_paise: 3000000, days: [1,2,3,4], stackable: false } }
      },
      currency: 'INR', approvedBy: 'user_madhu', isActive: false
    }
  })

  // ============================================================================
  // MEDIA & CONTENT
  // ============================================================================
  const mediaItems = [
    { id: 'media_bday_1', storageKey: 'studiox/birthday/bday_01.jpg', url: 'https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=1200&h=800&fit=crop', altText: 'Birthday celebration candid moment with cake cutting', tags: ['birthday', 'candid', 'celebration', 'cake'] },
    { id: 'media_bday_2', storageKey: 'studiox/birthday/bday_02.jpg', url: 'https://images.unsplash.com/photo-1464349095431-e9a21285b5c3?w=1200&h=800&fit=crop', altText: 'Children playing at birthday party', tags: ['birthday', 'children', 'outdoor', 'fun'] },
    { id: 'media_bday_3', storageKey: 'studiox/birthday/bday_03.jpg', url: 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=1200&h=800&fit=crop', altText: 'Birthday decorations and balloon setup', tags: ['birthday', 'decorations', 'balloons', 'venue'] },
    { id: 'media_maternity_1', storageKey: 'studiox/maternity/mat_01.jpg', url: 'https://images.unsplash.com/photo-1595899411377-591ce2e0b77f?w=1200&h=800&fit=crop', altText: 'Elegant maternity portrait in studio lighting', tags: ['maternity', 'studio', 'portrait', 'elegant'] },
    { id: 'media_maternity_2', storageKey: 'studiox/maternity/mat_02.jpg', url: 'https://images.unsplash.com/photo-1518821573096-f8dfa54462fc?w=1200&h=800&fit=crop', altText: 'Outdoor maternity shoot at golden hour', tags: ['maternity', 'outdoor', 'golden_hour', 'nature'] },
    { id: 'media_maternity_3', storageKey: 'studiox/maternity/mat_03.jpg', url: 'https://images.unsplash.com/photo-1515488766978-f037573d3d0e?w=1200&h=800&fit=crop', altText: 'Couple maternity session with partner', tags: ['maternity', 'couple', 'partner', 'love'] },
    { id: 'media_shower_1', storageKey: 'studiox/baby-shower/shower_01.jpg', url: 'https://images.unsplash.com/photo-1519183071298-a2962be91b0e?w=1200&h=800&fit=crop', altText: 'Baby shower decorations and gift table', tags: ['baby_shower', 'decorations', 'gifts', 'venue'] },
    { id: 'media_shower_2', storageKey: 'studiox/baby-shower/shower_02.jpg', url: 'https://images.unsplash.com/photo-1518831959646-742c3a14ebf7?w=1200&h=800&fit=crop', altText: 'Mother-to-be with family at baby shower', tags: ['baby_shower', 'family', 'mother', 'celebration'] },
    { id: 'media_shower_3', storageKey: 'studiox/baby-shower/shower_03.jpg', url: 'https://images.unsplash.com/photo-1519220845540-8a98dcb5a7d5?w=1200&h=800&fit=crop', altText: 'Baby shower games and candid moments', tags: ['baby_shower', 'games', 'candid', 'fun'] },
    { id: 'media_marriage_1', storageKey: 'studiox/marriage/mar_01.jpg', url: 'https://images.unsplash.com/photo-1519741497674-611481863552?w=1200&h=800&fit=crop', altText: 'Traditional Indian wedding ceremony', tags: ['marriage', 'traditional', 'ceremony', 'indian_wedding'] },
    { id: 'media_marriage_2', storageKey: 'studiox/marriage/mar_02.jpg', url: 'https://images.unsplash.com/photo-1537633264530-89cbd31b0b65?w=1200&h=800&fit=crop', altText: 'Bride and groom portrait session', tags: ['marriage', 'couple', 'portrait', 'bride_groom'] },
    { id: 'media_marriage_3', storageKey: 'studiox/marriage/mar_03.jpg', url: 'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=1200&h=800&fit=crop', altText: 'Wedding reception candid dance moment', tags: ['marriage', 'reception', 'dance', 'candid'] },
    { id: 'media_prewedding_1', storageKey: 'studiox/pre-wedding/pre_01.jpg', url: 'https://images.unsplash.com/photo-1583939003579-7bc0e3d72c9b?w=1200&h=800&fit=crop', altText: 'Pre-wedding couple shoot in scenic location', tags: ['pre_wedding', 'couple', 'outdoor', 'scenic'] },
    { id: 'media_prewedding_2', storageKey: 'studiox/pre-wedding/pre_02.jpg', url: 'https://images.unsplash.com/photo-1469371670807-013ccf25f193?w=1200&h=800&fit=crop', altText: 'Engagement ring close-up shot', tags: ['pre_wedding', 'engagement', 'ring', 'detail'] },
    { id: 'media_bts_1', storageKey: 'studiox/bts/bts_01.jpg', url: 'https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?w=1200&h=800&fit=crop', altText: 'Photographer at work during session', tags: ['behind_the_scenes', 'photographer', 'studio', 'work'] }
  ]

  for (const m of mediaItems) {
    await prisma.media.upsert({ where: { id: m.id }, update: {}, create: { id: m.id, tenantId: 'studiox', storageKey: m.storageKey, mediaType: 'image', url: m.url, altText: m.altText, tags: m.tags, rights: 'stock_placeholder', fileSizeBytes: 0, mimeType: 'image/jpeg', width: 1200, height: 800 } })
  }

  await Promise.all([
    prisma.contentPage.upsert({ where: { id: 'page_home' }, update: {}, create: { id: 'page_home', tenantId: 'studiox', route: '/', locale: 'en', title: 'Home', contentJson: { hero: { headline: 'Capturing Moments, Creating Memories', subtext: 'Professional photography for every occasion in Hyderabad', cta_text: 'Plan Your Shoot', cta_link: '/contact', background_media: 'media_bday_1' }, trust_indicators: [{ label: '500+ Events', icon: 'calendar' }, { label: '7+ Years', icon: 'award' }, { label: '100% Satisfaction', icon: 'heart' }], featured_occasions: ['birthday', 'maternity', 'baby-shower', 'marriage', 'full-marriage'] }, draftVersion: 1, publishedVersion: 1, status: 'published' } }),
    prisma.contentPage.upsert({ where: { id: 'page_about' }, update: {}, create: { id: 'page_about', tenantId: 'studiox', route: '/about', locale: 'en', title: 'About Us', contentJson: { story: 'Studiox was founded by Madhu Padishala with a passion for capturing life\'s most precious moments.', team: [{ name: 'Ramu', role: 'Lead Photographer', specialties: ['weddings', 'portraits', 'lighting_design'] }, { name: 'Venkatesh', role: 'Videographer', specialties: ['cinematic_films', 'same_day_edits', 'color_grading'] }, { name: 'Adithya', role: 'Associate Photographer', specialties: ['candid', 'events', 'drone'] }, { name: 'Guru', role: 'Lighting Tech', specialties: ['equipment', 'off_camera_flash', 'studio_setup'] }, { name: 'Natony', role: 'Album Designer', specialties: ['album_layout', 'fine_art_retouch', 'color_correction'] }, { name: 'Abdul', role: 'Coordinator', specialties: ['client_coordination', 'bts_content', 'backup_shooter'] }], values: [{ title: 'Authenticity', description: 'Real moments, real emotions' }, { title: 'Quality', description: 'Every pixel crafted with care' }, { title: 'Service', description: 'Your experience matters most' }] }, draftVersion: 1, publishedVersion: 1, status: 'published' } }),
    prisma.contentPage.upsert({ where: { id: 'page_services' }, update: {}, create: { id: 'page_services', tenantId: 'studiox', route: '/services', locale: 'en', title: 'Services', contentJson: { intro: 'From intimate maternity sessions to grand wedding celebrations, we have a package for every occasion.', packages: ['pkg_birthday', 'pkg_maternity', 'pkg_baby_shower', 'pkg_marriage', 'pkg_full_marriage'] }, draftVersion: 1, publishedVersion: 1, status: 'published' } }),
    prisma.contentPage.upsert({ where: { id: 'page_contact' }, update: {}, create: { id: 'page_contact', tenantId: 'studiox', route: '/contact', locale: 'en', title: 'Contact Us', contentJson: { address: 'Dilsukhnagar, Hyderabad, Telangana 500060', phone: '+917285988958', email: 'support@rungrow.in', whatsapp: '+917285988958', instagram: 'https://instagram.com/studioxphotograpghy', youtube: 'https://youtube.com/@mandatisreenath', service_areas: ['Dilsukhnagar', 'LB Nagar', 'Kothapet', 'Malakpet', 'Nagole', 'Chaithanyapuri', 'Saroor Nagar'] }, draftVersion: 1, publishedVersion: 1, status: 'published' } }),
    prisma.contentPage.upsert({ where: { id: 'page_privacy' }, update: {}, create: { id: 'page_privacy', tenantId: 'studiox', route: '/privacy', locale: 'en', title: 'Privacy Policy', contentJson: { content: 'Standard privacy policy template. Replace with legal-approved version.' }, draftVersion: 1, publishedVersion: 1, status: 'published' } })
  ])

  // ============================================================================
  // FAQ
  // ============================================================================
  const faqs = [
    { id: 'faq_1', question: 'How far in advance should I book my photography session?', answer: 'We recommend booking at least 2-4 weeks in advance for regular sessions (birthday, maternity, baby shower) and 3-6 months in advance for weddings. Popular dates during wedding season (Oct-Feb) fill up quickly. However, we do accommodate last-minute requests based on availability.', category: 'booking', displayOrder: 1 },
    { id: 'faq_2', question: 'What is your booking process?', answer: '1) Submit an enquiry via our website, WhatsApp, or Instagram. 2) Our AI assistant gathers your event details and checks availability. 3) You receive a detailed quote with package options. 4) Approve the quote and pay the advance to confirm your booking. 5) We send a contract for e-signature. 6) Your date is locked in!', category: 'booking', displayOrder: 2 },
    { id: 'faq_3', question: 'What is the advance payment to confirm a booking?', answer: 'For regular sessions: 25% of the package value. For weddings: ₹25,000 or 20% (whichever is higher). The balance is due on or before the event day. We accept UPI, card, and bank transfer via secure Razorpay payment links.', category: 'booking', displayOrder: 3 },
    { id: 'faq_4', question: 'What is included in the Full Marriage Coverage package (₹1,25,000)?', answer: 'Complete 2-day coverage (16 hours): 400+ edited photos, 15-minute cinematic film, 1-min teaser + 3-min highlight reel, 90-day online gallery, USB drive, 2x premium albums (12x12, 40pp), 2x parent albums (8x8, 20pp). Drone, second shooter, and same-day edit are included. Travel within 25km free.', category: 'packages', displayOrder: 4 },
    { id: 'faq_5', question: 'Can I customize a package or add specific services?', answer: 'Absolutely! All packages have add-ons: drone coverage (₹2,500-₹3,000), extra hours (₹2,000-₹3,000/hr), same-day edits, premium albums, second shooter, pre-wedding shoots. You can also request a custom quote for unique requirements.', category: 'packages', displayOrder: 5 },
    { id: 'faq_6', question: 'What is your travel policy for events outside Hyderabad?', answer: 'Free travel within included km (10-25km depending on package). Beyond that: ₹1,500-₹2,000/km. For outstation events >50km, client covers team travel and accommodation. Parking and tolls are always extra. We provide a detailed travel estimate with every quote.', category: 'packages', displayOrder: 6 },
    { id: 'faq_7', question: 'How long until I receive my photos and videos?', answer: 'Regular sessions: 7-10 business days for edited photos, 10-14 days for highlight reel. Weddings: 15-20 business days for photos, 20-30 days for cinematic film. Same-day edit add-on delivers a 3-min highlight film on the event day. Online gallery access starts immediately after delivery.', category: 'deliverables', displayOrder: 7 },
    { id: 'faq_8', question: 'Do you provide RAW files or only edited photos?', answer: 'We deliver only professionally edited, high-resolution JPEG files. RAW files are not included as they require professional editing software and our creative vision is applied during post-processing. All delivered photos are color-corrected and retouched to our quality standard.', category: 'deliverables', displayOrder: 8 },
    { id: 'faq_9', question: 'What is your cancellation and rescheduling policy?', answer: 'Rescheduling: Free if done >30 days before event (subject to date availability). Within 30 days: ₹5,000 fee. Cancellation: Advance is non-refundable. If we cancel due to emergency, full refund + 10% goodwill credit. Force majeure events handled case-by-case.', category: 'policies', displayOrder: 9 },
    { id: 'faq_10', question: 'Do you have backup equipment and backup photographers?', answer: 'Yes. Every shoot has backup camera bodies, lenses, batteries, and memory cards. For weddings, a second shooter is available as add-on (included in Full Marriage). In the rare event of photographer illness/emergency, our network of associate photographers ensures coverage.', category: 'policies', displayOrder: 10 }
  ]

  for (const f of faqs) {
    await prisma.faqEntry.upsert({ where: { id: f.id }, update: {}, create: { id: f.id, tenantId: 'studiox', question: f.question, answer: f.answer, category: f.category, displayOrder: f.displayOrder, isPublished: true } })
  }

  // ============================================================================
  // SEO LOCALITIES
  // ============================================================================
  const localities = [
    { id: 'loc_dilsukhnagar', locality: 'Dilsukhnagar', priority: 1, keywords: ['photographer dilsukhnagar', 'wedding photography dilsukhnagar', 'maternity shoot dilsukhnagar'] },
    { id: 'loc_lb_nagar', locality: 'LB Nagar', priority: 2, keywords: ['photographer lb nagar', 'birthday photography lb nagar', 'baby shower photography lb nagar'] },
    { id: 'loc_kothapet', locality: 'Kothapet', priority: 3, keywords: ['photographer kothapet', 'wedding photography kothapet'] },
    { id: 'loc_malakpet', locality: 'Malakpet', priority: 4, keywords: ['photographer malakpet', 'maternity shoot malakpet'] },
    { id: 'loc_nagole', locality: 'Nagole', priority: 5, keywords: ['photographer nagole', 'baby shower photography nagole'] },
    { id: 'loc_chaithanyapuri', locality: 'Chaithanyapuri', priority: 6, keywords: ['photographer chaithanyapuri'] },
    { id: 'loc_saroor_nagar', locality: 'Saroor Nagar', priority: 7, keywords: ['photographer saroor nagar'] }
  ]

  for (const l of localities) {
    await prisma.seoLocality.upsert({ where: { id: l.id }, update: {}, create: { id: l.id, tenantId: 'studiox', locality: l.locality, city: 'Hyderabad', state: 'Telangana', country: 'India', latitude: 17.3667, longitude: 78.5167, priority: l.priority, keywords: l.keywords, isActive: true } })
  }

  await prisma.seoSettings.upsert({
    where: { tenantId: 'studiox' },
    update: {},
    create: {
      tenantId: 'studiox', siteName: 'Studiox Photography', defaultTitle: 'Studiox | Professional Photography in Hyderabad', defaultDescription: 'Studiox Photography - Expert wedding, maternity, birthday & baby shower photography in Hyderabad. 500+ events captured. Book your session today.', ogImageUrl: 'https://images.unsplash.com/photo-1519741497674-611481863552?w=1200&h=630&fit=crop', twitterHandle: '@studioxphotograpghy', schemaType: 'Photographer', geoCoordinates: { latitude: 17.3667, longitude: 78.5167, address: 'Dilsukhnagar, Hyderabad, Telangana 500060' }
    }
  })

  // ============================================================================
  // CONNECTORS
  // ============================================================================
  await Promise.all([
    prisma.connectorConfig.upsert({ where: { id: 'conn_instagram' }, update: {}, create: { id: 'conn_instagram', tenantId: 'studiox', provider: 'instagram', configJson: { account_type: 'professional', handle: 'studioxphotograpghy', access_token: '[REPLACE_WITH_REAL_TOKEN]', refresh_token: '[REPLACE_WITH_REAL_TOKEN]', expires_at: null, permissions: ['instagram_basic', 'instagram_manage_comments', 'instagram_manage_insights', 'pages_show_list', 'pages_read_engagement'], webhook_verify_token: '[GENERATE_RANDOM]', capabilities: { comment_to_dm: true, dm_intake: true, lead_forms: true, click_to_whatsapp: true, campaign_sync: true } }, status: 'not_authorized' } }),
    prisma.connectorConfig.upsert({ where: { id: 'conn_youtube' }, update: {}, create: { id: 'conn_youtube', tenantId: 'studiox', provider: 'youtube', configJson: { channel_handle: '@mandatisreenath', channel_id: '[FETCH_FROM_API]', access_token: '[REPLACE_WITH_REAL_TOKEN]', refresh_token: '[REPLACE_WITH_REAL_TOKEN]', expires_at: null, permissions: ['youtube.readonly', 'youtube.force-ssl'], capabilities: { comment_monitoring: true, video_analytics: true, channel_insights: true } }, status: 'not_authorized' } }),
    prisma.connectorConfig.upsert({ where: { id: 'conn_whatsapp' }, update: {}, create: { id: 'conn_whatsapp', tenantId: 'studiox', provider: 'whatsapp', configJson: { phone_number_id: '[FROM_META_DEVELOPER]', waba_id: '[FROM_META_DEVELOPER]', access_token: '[REPLACE_WITH_REAL_TOKEN]', business_phone_number: '+917285988958', display_name: 'Studiox Photography', webhook_verify_token: '[GENERATE_RANDOM]', capabilities: { session_messages: true, template_messages: true, catalog_messages: true, interactive_messages: true, media_messages: true } }, status: 'not_authorized' } }),
    prisma.connectorConfig.upsert({ where: { id: 'conn_gbp' }, update: {}, create: { id: 'conn_gbp', tenantId: 'studiox', provider: 'google_business_profile', configJson: { place_id: null, account_id: '[REPLACE_IF_CLAIMED]', location_id: '[REPLACE_IF_CLAIMED]', access_token: '[REPLACE_WITH_REAL_TOKEN]', refresh_token: '[REPLACE_WITH_REAL_TOKEN]', expires_at: null, capabilities: { profile_updates: true, posts: true, photos: true, reviews: true, qa: true, insights: true } }, status: 'not_claimed' } })
  ])

  // ============================================================================
  // BUSINESS SETTINGS
  // ============================================================================
  await prisma.businessSettings.upsert({
    where: { tenantId: 'studiox' },
    update: {},
    create: {
      tenantId: 'studiox', settingsJson: {
        timezone: 'Asia/Kolkata', currency: 'INR', date_format: 'DD/MM/YYYY', time_format: 'HH:mm',
        working_hours: { monday: { open: '09:00', close: '19:00', closed: false }, tuesday: { open: '09:00', close: '19:00', closed: false }, wednesday: { open: '09:00', close: '19:00', closed: false }, thursday: { open: '09:00', close: '19:00', closed: false }, friday: { open: '09:00', close: '19:00', closed: false }, saturday: { open: '09:00', close: '19:00', closed: false }, sunday: { open: '10:00', close: '16:00', closed: false } },
        sla: { first_response_minutes: 120, quote_turnaround_hours: 4, followup_cadence_hours: [24, 72, 168] },
        notifications: { email_new_lead: true, whatsapp_new_lead: true, email_quote_approved: true, whatsapp_booking_confirmed: true, email_payment_received: true },
        ai_agent: { enabled: true, model: 'gpt-4o-mini', temperature: 0.3, max_tokens: 500, approval_threshold_paise: 5000000, discount_approval_threshold_pct: 10, escalation_keywords: ['complaint', 'refund', 'legal', 'urgent', 'emergency'] }
      }
    }
  })

  // ============================================================================
  // RESOURCES
  // ============================================================================
  await Promise.all([
    prisma.resource.upsert({ where: { id: 'res_ramu' }, update: {}, create: { id: 'res_ramu', tenantId: 'studiox', name: 'Ramu (Lead Photographer)', type: 'photographer', capacity: 1, description: 'Lead wedding & portrait photographer', metadata: { specialties: ['weddings', 'portraits', 'lighting'], user_id: 'user_ramu' }, isActive: true } }),
    prisma.resource.upsert({ where: { id: 'res_venkatesh' }, update: {}, create: { id: 'res_venkatesh', tenantId: 'studiox', name: 'Venkatesh (Videographer)', type: 'videographer', capacity: 1, description: 'Cinematic films & same-day edits', metadata: { specialties: ['cinematic', 'edits', 'color'], user_id: 'user_venkatesh' }, isActive: true } }),
    prisma.resource.upsert({ where: { id: 'res_adithya' }, update: {}, create: { id: 'res_adithya', tenantId: 'studiox', name: 'Adithya (Associate Photographer)', type: 'photographer', capacity: 1, description: 'Candid, events, drone certified', metadata: { specialties: ['candid', 'events', 'drone'], user_id: 'user_adithya', dgca_certified: true }, isActive: true } }),
    prisma.resource.upsert({ where: { id: 'res_studio_main' }, update: {}, create: { id: 'res_studio_main', tenantId: 'studiox', name: 'Main Studio Space', type: 'studio_space', capacity: 10, description: 'Fully equipped indoor studio with lighting', metadata: { area_sqft: 800, equipment: ['strobes', 'softboxes', 'backdrops', 'changing_room'] }, isActive: true } }),
    prisma.resource.upsert({ where: { id: 'res_drone_1' }, update: {}, create: { id: 'res_drone_1', tenantId: 'studiox', name: 'DJI Mavic 3 Pro', type: 'equipment', capacity: 1, description: 'Professional drone for aerial shots', metadata: { operator_required: 'res_adithya', dgca_registered: true }, isActive: true } })
  ])

  // ============================================================================
  // DEMO SCENARIO DATA (8-step acceptance test)
  // ============================================================================
  // Contact
  await prisma.contact.upsert({
    where: { id: 'contact_demo_priya' },
    update: {},
    create: { id: 'contact_demo_priya', tenantId: 'studiox', phoneE164: '+919876543210', emailNormalized: 'priya.sharma@email.com', displayName: 'Priya Sharma', consentState: 'marketing_opt_in', sourceFirst: 'instagram', sourceLast: 'instagram' }
  })

  // Lead
  await prisma.lead.upsert({
    where: { id: 'lead_demo_001' },
    update: {},
    create: { id: 'lead_demo_001', tenantId: 'studiox', contactId: 'contact_demo_priya', stage: 'won', score: 78, reasonsJson: { intent: 'high', event_date_match: true, budget_fit: true, source_quality: 'organic_social' }, ownerId: 'user_ramu', eventDate: new Date('2026-12-15'), budgetBand: '1L-2L', sourceFirst: 'instagram', sourceLast: 'instagram', utmJson: { source: 'instagram', medium: 'organic', campaign: 'diwali_2026' }, campaign: 'diwali_2026' }
  })

  // Inbound Event
  await prisma.inboundEvent.upsert({
    where: { id: 'evt_insta_demo_001' },
    update: {},
    create: { id: 'evt_insta_demo_001', tenantId: 'studiox', provider: 'instagram', providerEventId: 'inst_evt_17892345678901234', eventType: 'comment_reply', externalActorId: 'ig_user_demo_123', occurredAt: new Date('2026-11-05T10:30:00Z'), sourceAssetId: 'reel_diwali_2026', campaign: 'diwali_2026', utm: { source: 'instagram', medium: 'organic', campaign: 'diwali_2026' }, payloadRef: 's3://tenant-assets/studiox/inbound/instagram/evt_insta_demo_001.json', consentEvidence: { type: 'comment_reply', policy: 'legitimate_interest', comment_text: 'Price for full marriage coverage?', reply_text: 'DM sent with details' }, state: 'lead_upserted', processedAt: new Date() }
  })

  // Conversation & Messages
  await prisma.conversation.upsert({ where: { id: 'conv_demo_001' }, update: {}, create: { id: 'conv_demo_001', tenantId: 'studiox', leadId: 'lead_demo_001', channel: 'instagram_dm', status: 'open', providerConversationId: 'ig_conv_demo_123' } })

  await Promise.all([
    prisma.message.upsert({ where: { id: 'msg_1' }, update: {}, create: { id: 'msg_1', tenantId: 'studiox', conversationId: 'conv_demo_001', leadId: 'lead_demo_001', channel: 'instagram_dm', direction: 'inbound', content: 'Can you cover candid and traditional photography for 300 guests at a farmhouse on December 15?', providerMessageId: 'ig_msg_001', status: 'delivered', eventAt: new Date('2026-11-05T10:31:00Z'), metadataJson: { ai_extracted: { occasion: 'wedding', guest_count: 300, venue_type: 'farmhouse', date: '2026-12-15', preferred_coverage: ['candid', 'traditional'] } } } }),
    prisma.message.upsert({ where: { id: 'msg_2' }, update: {}, create: { id: 'msg_2', tenantId: 'studiox', conversationId: 'conv_demo_001', leadId: 'lead_demo_001', channel: 'instagram_dm', direction: 'outbound', content: 'Yes, we have options for this type of event. I can recommend a full-day candid and traditional package or a shorter package with album coverage. Which farmhouse is it, and would you like video coverage too?', providerMessageId: 'ig_msg_002', status: 'delivered', eventAt: new Date('2026-11-05T10:31:05Z'), metadataJson: { tool_calls: [{ tool: 'check_availability', arguments: { occasion: 'wedding', date_range: ['2026-12-15'], duration_hours: 8 }, result: { available: true, slots: [{ resource: 'res_ramu', start: '2026-12-15T09:00:00', end: '2026-12-15T17:00:00' }] } }], ai_extracted: {} } } }),
    prisma.message.upsert({ where: { id: 'msg_3' }, update: {}, create: { id: 'msg_3', tenantId: 'studiox', conversationId: 'conv_demo_001', leadId: 'lead_demo_001', channel: 'instagram_dm', direction: 'inbound', content: 'It is Farmhouse X in Shamirpet. Yes, we want both photography and videography.', providerMessageId: 'ig_msg_003', status: 'delivered', eventAt: new Date('2026-11-05T10:32:00Z'), metadataJson: { ai_extracted: { venue: 'Farmhouse X Shamirpet', wants_video: true } } } }),
    prisma.message.upsert({ where: { id: 'msg_4' }, update: {}, create: { id: 'msg_4', tenantId: 'studiox', conversationId: 'conv_demo_001', leadId: 'lead_demo_001', channel: 'instagram_dm', direction: 'outbound', content: 'Great! For Farmhouse X (≈28km from studio), I have two packages that fit:\n\n1. **Marriage Photography (₹21,999)** - 6 hrs, 150 photos, 5-min film, teaser. Travel: ₹2,600 extra.\n2. **Full Marriage Coverage (₹1,25,000)** - 2 days/16 hrs, 400 photos, 15-min film, 2 premium albums + parent albums. Travel included.\n\nBoth include drone. Which appeals more? I can hold a slot while you decide.', providerMessageId: 'ig_msg_004', status: 'delivered', eventAt: new Date('2026-11-05T10:32:10Z'), metadataJson: { tool_calls: [{ tool: 'calculate_quote', arguments: { leadId: 'lead_demo_001', packageId: 'pkg_marriage', addOns: ['addon_drone'], eventDate: '2026-12-15', location: 'Farmhouse X Shamirpet' }, result: { quoteId: 'quote_demo_001', totalPaise: 2459900 } }, { tool: 'calculate_quote', arguments: { leadId: 'lead_demo_001', packageId: 'pkg_full_marriage', addOns: [], eventDate: '2026-12-15', location: 'Farmhouse X Shamirpet' }, result: { quoteId: 'quote_demo_002', totalPaise: 12500000 } }], ai_extracted: {} } } })
  ])

  // Quotes
  await Promise.all([
    prisma.quote.upsert({ where: { id: 'quote_demo_001' }, update: {}, create: { id: 'quote_demo_001', tenantId: 'studiox', leadId: 'lead_demo_001', revision: 1, status: 'approved', pricebookVersion: 1, totalsJson: { items: [{ package_id: 'pkg_marriage', name: 'Marriage Photography', base_paise: 2199900, quantity: 1 }, { addon_id: 'addon_drone', name: 'Drone Coverage', base_paise: 300000, quantity: 1 }, { name: 'Travel (28km @ ₹2,000/km beyond 15km)', base_paise: 26000, quantity: 1 }], subtotal_paise: 2525900, discount_paise: 0, tax_paise: 0, total_paise: 2459900, currency: 'INR' }, expiresAt: new Date('2026-11-12T23:59:59Z'), approvedBy: 'user_madhu', approvedAt: new Date() } }),
    prisma.quote.upsert({ where: { id: 'quote_demo_002' }, update: {}, create: { id: 'quote_demo_002', tenantId: 'studiox', leadId: 'lead_demo_001', revision: 1, status: 'approved', pricebookVersion: 1, totalsJson: { items: [{ package_id: 'pkg_full_marriage', name: 'Full Marriage Coverage', base_paise: 12500000, quantity: 1 }], subtotal_paise: 12500000, discount_paise: 0, tax_paise: 0, total_paise: 12500000, currency: 'INR' }, expiresAt: new Date('2026-11-12T23:59:59Z'), approvedBy: 'user_madhu', approvedAt: new Date() } })
  ])

  await Promise.all([
    prisma.quoteItem.upsert({ where: { id: 'qi_001' }, update: {}, create: { id: 'qi_001', quoteId: 'quote_demo_001', packageId: 'pkg_marriage', name: 'Marriage Photography', basePricePaise: 2199900, quantity: 1, lineTotalPaise: 2199900 } }),
    prisma.quoteItem.upsert({ where: { id: 'qi_002' }, update: {}, create: { id: 'qi_002', quoteId: 'quote_demo_001', addonId: 'addon_drone', name: 'Drone Coverage', basePricePaise: 300000, quantity: 1, lineTotalPaise: 300000 } }),
    prisma.quoteItem.upsert({ where: { id: 'qi_003' }, update: {}, create: { id: 'qi_003', quoteId: 'quote_demo_001', name: 'Travel (28km)', basePricePaise: 26000, quantity: 1, lineTotalPaise: 26000 } }),
    prisma.quoteItem.upsert({ where: { id: 'qi_004' }, update: {}, create: { id: 'qi_004', quoteId: 'quote_demo_002', packageId: 'pkg_full_marriage', name: 'Full Marriage Coverage', basePricePaise: 12500000, quantity: 1, lineTotalPaise: 12500000 } })
  ])

  // Slot Holds
  await Promise.all([
    prisma.slotHold.upsert({ where: { id: 'hold_demo_001' }, update: {}, create: { id: 'hold_demo_001', tenantId: 'studiox', resourceId: 'res_ramu', leadId: 'lead_demo_001', startsAt: new Date('2026-12-15T09:00:00Z'), endsAt: new Date('2026-12-15T17:00:00Z'), ttlMinutes: 30, state: 'converted', holdIdempotencyKey: 'hold_lead_demo_001_res_ramu_20261215_090000', expiresAt: new Date('2026-12-15T09:30:00Z') } }),
    prisma.slotHold.upsert({ where: { id: 'hold_demo_002' }, update: {}, create: { id: 'hold_demo_002', tenantId: 'studiox', resourceId: 'res_venkatesh', leadId: 'lead_demo_001', startsAt: new Date('2026-12-15T09:00:00Z'), endsAt: new Date('2026-12-15T17:00:00Z'), ttlMinutes: 30, state: 'converted', holdIdempotencyKey: 'hold_lead_demo_001_res_venkatesh_20261215_090000', expiresAt: new Date('2026-12-15T09:30:00Z') } })
  ])

  // Payment
  await prisma.payment.upsert({
    where: { id: 'pay_demo_001' },
    update: {},
    create: { id: 'pay_demo_001', tenantId: 'studiox', quoteId: 'quote_demo_002', razorpayOrderId: 'order_demo_001', razorpayPaymentId: 'pay_demo_001', amountPaise: 12500000, currency: 'INR', status: 'captured', method: 'upi', capturedAt: new Date(), feePaise: 250000, netPaise: 12250000, idempotencyKey: 'pay_lead_demo_001_quote_demo_002', ledgerSyncedAt: new Date() }
  })

  // Bookings
  await Promise.all([
    prisma.booking.upsert({ where: { id: 'booking_demo_001' }, update: {}, create: { id: 'booking_demo_001', tenantId: 'studiox', resourceId: 'res_ramu', customerId: 'contact_demo_priya', quoteId: 'quote_demo_002', startsAt: new Date('2026-12-15T09:00:00Z'), endsAt: new Date('2026-12-15T17:00:00Z'), state: 'confirmed', paymentId: 'pay_demo_001', confirmedBy: 'user_madhu', confirmedAt: new Date() } }),
    prisma.booking.upsert({ where: { id: 'booking_demo_002' }, update: {}, create: { id: 'booking_demo_002', tenantId: 'studiox', resourceId: 'res_venkatesh', customerId: 'contact_demo_priya', quoteId: 'quote_demo_002', startsAt: new Date('2026-12-15T09:00:00Z'), endsAt: new Date('2026-12-15T17:00:00Z'), state: 'confirmed', paymentId: 'pay_demo_001', confirmedBy: 'user_madhu', confirmedAt: new Date() } })
  ])

  // Attribution Events
  await Promise.all([
    prisma.attributionEvent.upsert({ where: { id: 'attr_1' }, update: {}, create: { id: 'attr_1', tenantId: 'studiox', leadId: 'lead_demo_001', touchpointSeq: 1, channel: 'instagram', campaign: 'diwali_2026', utmJson: { source: 'instagram', medium: 'organic', campaign: 'diwali_2026' }, modelWeightsJson: { first_touch: 1.0, last_touch: 0.0, linear: 0.5, time_decay: 0.6, u_shaped: 0.4 }, revenueAttributedPaise: 12500000, occurredAt: new Date('2026-11-05T10:30:00Z') } }),
    prisma.attributionEvent.upsert({ where: { id: 'attr_2' }, update: {}, create: { id: 'attr_2', tenantId: 'studiox', leadId: 'lead_demo_001', touchpointSeq: 2, channel: 'instagram_dm', campaign: 'diwali_2026', utmJson: { source: 'instagram', medium: 'dm', campaign: 'diwali_2026' }, modelWeightsJson: { first_touch: 0.0, last_touch: 1.0, linear: 0.5, time_decay: 0.4, u_shaped: 0.6 }, revenueAttributedPaise: 12500000, occurredAt: new Date('2026-11-05T10:31:00Z') } })
  ])

  // Audit Events
  await Promise.all([
    prisma.auditEvent.upsert({ where: { id: 'audit_1' }, update: {}, create: { id: 'audit_1', tenantId: 'studiox', actorId: 'system', action: 'lead_created', entityType: 'lead', entityId: 'lead_demo_001', beforeAfterRef: { after: { stage: 'new', source: 'instagram' } } } }),
    prisma.auditEvent.upsert({ where: { id: 'audit_2' }, update: {}, create: { id: 'audit_2', tenantId: 'studiox', actorId: 'user_madhu', action: 'quote_approved', entityType: 'quote', entityId: 'quote_demo_002', beforeAfterRef: { before: { status: 'pending_approval' }, after: { status: 'approved' } } } }),
    prisma.auditEvent.upsert({ where: { id: 'audit_3' }, update: {}, create: { id: 'audit_3', tenantId: 'studiox', actorId: 'system', action: 'payment_captured', entityType: 'payment', entityId: 'pay_demo_001', beforeAfterRef: { after: { status: 'captured', amount_paise: 12500000 } } } }),
    prisma.auditEvent.upsert({ where: { id: 'audit_4' }, update: {}, create: { id: 'audit_4', tenantId: 'studiox', actorId: 'user_madhu', action: 'booking_confirmed', entityType: 'booking', entityId: 'booking_demo_001', beforeAfterRef: { after: { state: 'confirmed', payment_id: 'pay_demo_001' } } } })
  ])

  // Consent Event
  await prisma.consentEvent.upsert({
    where: { id: 'consent_demo_001' },
    update: {},
    create: { id: 'consent_demo_001', tenantId: 'studiox', subjectId: 'contact_demo_priya', subjectType: 'contact', purpose: 'marketing_communications', proofRef: { source: 'instagram_comment_reply', comment_id: 'inst_evt_17892345678901234', timestamp: '2026-11-05T10:30:00Z', ip_hash: 'sha256:abc123' }, status: 'granted', expiresAt: new Date('2027-11-05T10:30:00Z') }
  })

  // Connector Health
  await Promise.all([
    prisma.connectorHealth.upsert({ where: { id: 'health_instagram' }, update: {}, create: { id: 'health_instagram', tenantId: 'studiox', provider: 'instagram', status: 'configured', lastSuccessAt: null, errorRate5m: 0, errorRate24h: 0, quotaRemaining: 1000, checkedAt: new Date() } }),
    prisma.connectorHealth.upsert({ where: { id: 'health_youtube' }, update: {}, create: { id: 'health_youtube', tenantId: 'studiox', provider: 'youtube', status: 'configured', lastSuccessAt: null, errorRate5m: 0, errorRate24h: 0, quotaRemaining: 10000, checkedAt: new Date() } }),
    prisma.connectorHealth.upsert({ where: { id: 'health_whatsapp' }, update: {}, create: { id: 'health_whatsapp', tenantId: 'studiox', provider: 'whatsapp', status: 'configured', lastSuccessAt: null, errorRate5m: 0, errorRate24h: 0, quotaRemaining: 1000, checkedAt: new Date() } }),
    prisma.connectorHealth.upsert({ where: { id: 'health_gbp' }, update: {}, create: { id: 'health_gbp', tenantId: 'studiox', provider: 'google_business_profile', status: 'not_claimed', lastSuccessAt: null, errorRate5m: 0, errorRate24h: 0, quotaRemaining: 0, checkedAt: new Date() } })
  ])

  console.log('✅ Studiox demo data seeded successfully!')
  console.log('📊 Created: Tenant, Users, Packages, Media, FAQs, SEO, Connectors, Resources, Demo Scenario')
}

main()
  .catch((e) => {
    console.error('❌ Seed failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })