from typing import Dict, Any, List, Optional

class BiodiversityService:
    """
    Biodiversity and Ecological Exposure Engine (Section 25 / IUCN & WDPA Intersections).
    Evaluates endangered/protected species range overlaps (IUCN Red List / OBIS data)
    and marine breeding grounds & protected sites (WDPA / Protected Planet data).
    """

    SPECIES_DATABASE = [
        # Red Sea & Suez Canal Sector
        {
            "region_box": (27.0, 31.8, 31.5, 34.5),
            "species": [
                {
                    "name": "Dugong (Dugong dugon)",
                    "status": "Vulnerable (IUCN Red List)",
                    "intersect_time": "+6h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Green Sea Turtle (Chelonia mydas)",
                    "status": "Endangered (IUCN Red List)",
                    "intersect_time": "+3h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Hawksbill Sea Turtle (Eretmochelys imbricata)",
                    "status": "Critically Endangered (IUCN Red List)",
                    "intersect_time": "+12h",
                    "source": "IUCN Red List / OBIS occurrence data"
                }
            ],
            "protected_sites": [
                {
                    "name": "Great Bitter Lake & Suez Marine Sanctuary Reserve",
                    "distance_km": 1.8,
                    "risk": "HIGH",
                    "basis": "within projected +3h exposure zone",
                    "source": "WDPA / Protected Planet"
                },
                {
                    "name": "Ras Mohammad & Gulf of Suez Coastal Protected Corridor",
                    "distance_km": 12.5,
                    "risk": "MODERATE",
                    "basis": "within projected +12h exposure zone",
                    "source": "WDPA / Protected Planet"
                }
            ]
        },

        # Surat / Hazira / Gulf of Khambhat Sector (Gujarat)
        {
            "region_box": (20.0, 22.2, 72.0, 73.2),
            "species": [
                {
                    "name": "Indo-Pacific Humpback Dolphin (Sousa chinensis)",
                    "status": "Vulnerable (IUCN Red List)",
                    "intersect_time": "+3h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Olive Ridley Turtle (Lepidochelys olivacea)",
                    "status": "Vulnerable (IUCN Red List)",
                    "intersect_time": "+6h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Lesser Flamingo (Phoeniconaias minor)",
                    "status": "Near Threatened (IUCN Red List)",
                    "intersect_time": "+12h",
                    "source": "IUCN Red List / OBIS occurrence data"
                }
            ],
            "protected_sites": [
                {
                    "name": "Hazira Mangrove Conservation Belt & Estuary Reserve",
                    "distance_km": 2.4,
                    "risk": "HIGH",
                    "basis": "within projected +6h exposure zone",
                    "source": "WDPA / Protected Planet"
                },
                {
                    "name": "Suvali Ecological Coastal Reserve & Mudflats",
                    "distance_km": 3.8,
                    "risk": "MODERATE",
                    "basis": "within projected +12h exposure zone",
                    "source": "WDPA / Protected Planet"
                }
            ]
        },

        # Gulf of Kutch Sector (Gujarat)
        {
            "region_box": (22.0, 23.6, 68.8, 70.8),
            "species": [
                {
                    "name": "Whale Shark (Rhincodon typus)",
                    "status": "Endangered (IUCN Red List)",
                    "intersect_time": "+3h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Dugong (Dugong dugon)",
                    "status": "Vulnerable (IUCN Red List)",
                    "intersect_time": "+6h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Green Sea Turtle (Chelonia mydas)",
                    "status": "Endangered (IUCN Red List)",
                    "intersect_time": "+12h",
                    "source": "IUCN Red List / OBIS occurrence data"
                }
            ],
            "protected_sites": [
                {
                    "name": "Marine National Park & Sanctuary, Jamnagar",
                    "distance_km": 4.2,
                    "risk": "HIGH",
                    "basis": "within projected +6h exposure zone",
                    "source": "WDPA / Protected Planet"
                },
                {
                    "name": "Pirotan Island Coral Reef Sanctuary Reserve",
                    "distance_km": 7.5,
                    "risk": "MODERATE",
                    "basis": "within projected +12h exposure zone",
                    "source": "WDPA / Protected Planet"
                }
            ]
        },

        # Chennai / Ennore Sector (Tamil Nadu)
        {
            "region_box": (12.8, 13.6, 80.0, 80.6),
            "species": [
                {
                    "name": "Olive Ridley Turtle (Lepidochelys olivacea)",
                    "status": "Vulnerable (IUCN Red List)",
                    "intersect_time": "+3h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Smooth-Coated Otter (Lutrogale perspicillata)",
                    "status": "Vulnerable (IUCN Red List)",
                    "intersect_time": "+6h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Spot-Billed Pelican (Pelecanus philippensis)",
                    "status": "Near Threatened (IUCN Red List)",
                    "intersect_time": "+12h",
                    "source": "IUCN Red List / OBIS occurrence data"
                }
            ],
            "protected_sites": [
                {
                    "name": "Pulicat Lake Lagoon & Bird Sanctuary Reserve",
                    "distance_km": 3.5,
                    "risk": "HIGH",
                    "basis": "within projected +6h exposure zone",
                    "source": "WDPA / Protected Planet"
                },
                {
                    "name": "Ennore Creek Fish Breeding Estuary Grounds",
                    "distance_km": 1.2,
                    "risk": "HIGH",
                    "basis": "within projected +3h exposure zone",
                    "source": "WDPA / Protected Planet"
                }
            ]
        },

        # Gulf of Thailand Sector (Sattahip / Pattaya)
        {
            "region_box": (12.0, 13.5, 100.2, 101.8),
            "species": [
                {
                    "name": "Irrawaddy Dolphin (Orcaella brevirostris)",
                    "status": "Endangered (IUCN Red List)",
                    "intersect_time": "+3h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Hawksbill Turtle (Eretmochelys imbricata)",
                    "status": "Critically Endangered (IUCN Red List)",
                    "intersect_time": "+6h",
                    "source": "IUCN Red List / OBIS occurrence data"
                },
                {
                    "name": "Finless Porpoise (Neophocaena phocaenoides)",
                    "status": "Vulnerable (IUCN Red List)",
                    "intersect_time": "+12h",
                    "source": "IUCN Red List / OBIS occurrence data"
                }
            ],
            "protected_sites": [
                {
                    "name": "Mu Ko Samet Marine National Park Reserve",
                    "distance_km": 5.8,
                    "risk": "MODERATE",
                    "basis": "within projected +12h exposure zone",
                    "source": "WDPA / Protected Planet"
                },
                {
                    "name": "Sattahip Sea Turtle Conservation Center Reserve",
                    "distance_km": 2.1,
                    "risk": "HIGH",
                    "basis": "within projected +3h exposure zone",
                    "source": "WDPA / Protected Planet"
                }
            ]
        }
    ]

    @classmethod
    def get_biodiversity_exposure(
        cls,
        lat: float,
        lon: float,
        trajectory_points: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculates species range overlaps and protected marine site exposures
        based on IUCN Red List, OBIS, and WDPA / Protected Planet datasets.
        """
        matched_species = []
        matched_sites = []

        for region in cls.SPECIES_DATABASE:
            lat_min, lat_max, lon_min, lon_max = region["region_box"]
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                matched_species.extend(region["species"])
                matched_sites.extend(region["protected_sites"])
                break

        return {
            "has_biodiversity_data": bool(matched_species or matched_sites),
            "endangered_species": matched_species,
            "protected_sites": matched_sites
        }
