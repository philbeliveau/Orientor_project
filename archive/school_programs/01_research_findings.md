# School Programs Research Findings

## Executive Summary

This document contains comprehensive research findings for integrating CEGEP and university program banks into the Orientor platform. The research covers data sources, APIs, integration strategies, and implementation recommendations.

## CEGEP Programs in Quebec

### Key Findings
- **48 public CEGEPs** and ~70 private colleges across Quebec
- **No direct public APIs** available, but multiple data access methods identified
- **Données Québec CKAN API** provides the most structured access to educational datasets
- **SRAM (Service régional d'admission)** manages 32 CEGEPs with comprehensive program directory

### Official Data Sources

#### 1. Données Québec (Primary Source)
- **URL**: https://www.donneesquebec.ca/
- **API Type**: CKAN-based REST API
- **Endpoint**: `https://www.donneesquebec.ca/recherche/api/3/action/package_search`
- **Authentication**: None required
- **Rate Limits**: Not specified
- **Data Formats**: CSV, JSON, XML, HTML, PDF
- **Content**: 29 education-related datasets

#### 2. SRAM (Service régional d'admission)
- **URL**: https://www.sram.qc.ca/en
- **Coverage**: 32 CEGEPs and public colleges
- **Programs**: 100+ program applications
- **Access Method**: Web scraping (no public API)
- **Languages**: French/English bilingual

#### 3. Institut de la statistique du Québec (ISQ)
- **URL**: https://statistique.quebec.ca/en/statistiques/par-themes/education
- **Access Type**: Research data services (authorization required)
- **Data Quality**: Highest available
- **Coverage**: Administrative and survey data

### Program Structure

#### Pre-University Programs (DEC Pré-universitaire)
- **Duration**: 2 years full-time
- **Purpose**: University preparation
- **Examples**: Sciences, Social Sciences, Arts & Literature

#### Technical Programs (DEC Technique)
- **Duration**: 3 years full-time
- **Purpose**: Job market preparation + university access
- **Count**: 133 technical programs across 5 broad fields
- **Notable Programs**: 
  - Dental Hygiene (111A0)
  - 3D Animation and CGI (574B0)
  - Accounting and Management Technology (410B0)

#### Popular Program Categories
1. Administration, Commerce and Computer Technology
2. Health Services
3. Engineering and Technology
4. Arts and Communications
5. Natural Sciences

### Integration Recommendations for CEGEPs

#### Phase 1: Immediate Implementation
1. **CKAN API Integration**: Connect to Données Québec for educational statistics
2. **Web Scraping**: Develop scrapers for SRAM program directory
3. **Static Data Import**: Regular updates from government program listings

#### Phase 2: Advanced Integration
1. **Institutional Partnerships**: Direct relationships with SRAM and major CEGEPs
2. **Research Collaboration**: Partner with ISQ for comprehensive data access
3. **Data Standardization**: Create unified CEGEP program database

## University Program Banks

### Key Canadian Sources

#### 1. Statistics Canada CIP 2021
- **URL**: https://www.statcan.gc.ca/en/subjects/standard/cip/2021/index
- **Coverage**: Official Canadian program classification system
- **Access**: Open data, no authentication required
- **Updates**: 10-year revision cycle
- **Integration**: Direct download and API access available

#### 2. ESDC CPIC Database (Powers EduCanada)
- **URL**: https://www.educanada.ca/
- **Coverage**: Comprehensive Canadian university and college programs
- **Access Method**: Search interface (API investigation needed)
- **Languages**: Multilingual support

#### 3. University of Waterloo Open Data API
- **URL**: https://uwaterloo.ca/api/
- **API Type**: REST API with 40+ endpoints
- **Authentication**: API key required
- **Rate Limits**: Institutional policies apply
- **Coverage**: Courses, programs, schedules, admissions

### Major International APIs

#### 1. US College Scorecard API
- **URL**: https://collegescorecard.ed.gov/data/
- **Coverage**: 7,000+ US institutions
- **API Endpoint**: `https://api.data.gov/ed/collegescorecard/v1/schools`
- **Authentication**: API key required (api.data.gov)
- **Rate Limits**: 1,000 requests per hour
- **Data Format**: JSON

#### 2. HESA (UK Higher Education Statistics)
- **URL**: https://www.hesa.ac.uk/data-and-analysis
- **License**: Creative Commons
- **Coverage**: UK higher education institutions
- **Access**: Open data downloads, potential API development

#### 3. ETER (European Higher Education)
- **URL**: https://www.eter-project.com/
- **Coverage**: 3,500+ European higher education institutions
- **Data Format**: CSV, Excel
- **Access**: Registration required for full dataset

### University-Specific APIs

#### 1. Stanford Student API
- **Endpoint**: https://students.stanford.edu/api/
- **Format**: XML
- **Content**: Course catalogs, enrollment data
- **Authentication**: Institutional access required

#### 2. Harvard University APIs
- **Platform**: Multiple specialized APIs
- **Notable**: Course planner, library data
- **Access**: Varies by API

### Classification Systems

#### 1. CIP (Classification of Instructional Programs)
- **Scope**: Canada and United States
- **Structure**: Hierarchical coding system
- **Maintenance**: Statistics Canada / US Department of Education
- **Updates**: Every 10 years

#### 2. ISCED (International Standard Classification of Education)
- **Scope**: UNESCO standard used by 100+ countries
- **Purpose**: International comparability
- **Integration**: Crosswalk mappings available

## Implementation Strategy

### Phase 1: Foundation (Month 1-2)
1. Integrate College Scorecard API for US university data
2. Implement Statistics Canada CIP for Canadian program classification
3. Set up web scraping for SRAM CEGEP data
4. Create basic program search functionality

### Phase 2: Expansion (Month 3-4)
1. Add University of Waterloo API for detailed Canadian data
2. Integrate HESA open data for UK coverage
3. Implement Quebec open data CKAN API
4. Enhance search with advanced filtering

### Phase 3: Optimization (Month 5-6)
1. Add institutional partnerships where possible
2. Implement data validation and quality checks
3. Create comprehensive program recommendation engine
4. Add multilingual support (French/English minimum)

## Technical Requirements

### API Integration Specifications
- **Authentication**: Support for API keys, OAuth 2.0, institutional access
- **Rate Limiting**: Implement respectful request patterns (1 req/sec default)
- **Data Formats**: JSON (primary), CSV, XML support
- **Caching**: Implement local caching for frequently accessed data
- **Error Handling**: Robust retry mechanisms and fallback options

### Data Schema Requirements
- **Program Classification**: Support for CIP, ISCED codes
- **Multilingual Content**: French/English minimum, expandable
- **Geographic Data**: Country, province/state, city information
- **Institution Details**: Name, type, accreditation status
- **Program Details**: Duration, prerequisites, outcomes

### Scalability Considerations
- **Database Design**: Optimized for program search and filtering
- **Search Performance**: Elasticsearch or similar for text search
- **Update Frequency**: Daily for dynamic content, weekly for static
- **Geographic Distribution**: CDN for global access

## Risk Assessment

### High Risk
- **API Changes**: External APIs may change without notice
- **Rate Limiting**: Aggressive limits could impact user experience
- **Data Quality**: Inconsistent or outdated program information

### Medium Risk
- **Legal Compliance**: Web scraping terms of service
- **Authentication**: Loss of API access credentials
- **Performance**: High load on external services

### Mitigation Strategies
- **Multiple Sources**: Never rely on single data provider
- **Local Caching**: Maintain local copies of critical data
- **Monitoring**: Automated health checks for all data sources
- **Partnerships**: Formal agreements where possible

## Next Steps

1. **Technical Architecture**: Design detailed system architecture
2. **API Implementation**: Start with highest-value, lowest-risk integrations
3. **Data Pipeline**: Create automated data ingestion and validation
4. **User Interface**: Design program search and discovery experience
5. **Testing Strategy**: Comprehensive testing of all data sources

## Appendix: Resource URLs

### Canadian Sources
- Statistics Canada CIP: https://www.statcan.gc.ca/en/subjects/standard/cip/2021/index
- EduCanada: https://www.educanada.ca/
- Données Québec: https://www.donneesquebec.ca/
- SRAM: https://www.sram.qc.ca/en

### International APIs  
- College Scorecard: https://collegescorecard.ed.gov/data/
- University of Waterloo: https://uwaterloo.ca/api/
- HESA: https://www.hesa.ac.uk/data-and-analysis
- ETER: https://www.eter-project.com/

### Standards and Classification
- CIP 2021: https://www.statcan.gc.ca/en/subjects/standard/cip/2021/index
- ISCED: http://uis.unesco.org/en/topic/international-standard-classification-education-isced