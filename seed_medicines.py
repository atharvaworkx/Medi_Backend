from medicines.models import Medicine

def seed_medicines():
    medicines = [
        {
            'name': 'Ashwagandha Churna',
            'category': 'ayurvedic',
            'description': 'Helps reduce stress and anxiety while boosting energy levels.',
            'dosage_info': '1 tsp with warm milk before bed.',
            'dosha_affinity': 'vata',
            'price': 250.00,
            'stock_quantity': 50
        },
        {
            'name': 'Triphala Tablets',
            'category': 'ayurvedic',
            'description': 'Supports digestion and detoxification of the intestinal tract.',
            'dosage_info': '2 tablets with water daily.',
            'dosha_affinity': 'general',
            'price': 180.00,
            'stock_quantity': 100
        },
        {
            'name': 'Brahmi Ghrita',
            'category': 'herbal',
            'description': 'Ayurvedic medicated ghee for memory and cognitive health.',
            'dosage_info': '1/2 tsp twice a day on empty stomach.',
            'dosha_affinity': 'pitta',
            'price': 450.00,
            'stock_quantity': 30
        },
        {
            'name': 'Chyawanprash Special',
            'category': 'ayurvedic',
            'description': 'Immunity booster rich in Vitamin C and antioxidants.',
            'dosage_info': '1 tbsp daily with warm milk.',
            'dosha_affinity': 'general',
            'price': 320.00,
            'stock_quantity': 75
        },
        {
            'name': 'Shatavari Kalpa',
            'category': 'herbal',
            'description': 'Traditional tonic for female reproductive health and vitality.',
            'dosage_info': '2 tsp with milk twice daily.',
            'dosha_affinity': 'pitta',
            'price': 290.00,
            'stock_quantity': 40
        }
    ]
    
    for m_data in medicines:
        name = m_data.pop('name')
        Medicine.objects.get_or_create(name=name, defaults=m_data)
    
    print("Medicines seeded successfully!")

if __name__ == "__main__":
    seed_medicines()
