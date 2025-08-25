#!/usr/bin/env python3
"""
Jim's Marketing Generator
An advanced Flask app that generates personalized marketing content using Google Gemini
with comprehensive company research and industry analysis
"""

import os
import re
import time
import json
from urllib.parse import urljoin, urlparse
from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from document_generator import generate_marketing_document
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Google Gemini API
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is required")

genai.configure(api_key=gemini_api_key)

# Initialize Gemini model
def get_gemini_model():
    """Get configured Gemini model instance"""
    return genai.GenerativeModel('gemini-2.0-flash-exp')

def clean_markdown_formatting(text):
    """Remove markdown formatting characters and fix spacing issues to ensure clean copy-paste text"""
    if not text:
        return text
    
    import re
    
    # Remove bold markdown (**text**)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # Remove italic markdown (*text*)
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)', r'\1', text)
    
    # Remove header markdown (# text)
    text = re.sub(r'^#+\s*(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Remove any remaining standalone asterisks or double asterisks
    text = re.sub(r'\*+', '', text)
    
    # Fix numbered list formatting - remove extra spaces/tabs after numbers
    text = re.sub(r'^(\d+\.\s+)\s+', r'\1', text, flags=re.MULTILINE)
    
    # Remove excessive indentation at start of lines (but preserve normal paragraph spacing)
    text = re.sub(r'^[ \t]{3,}', '', text, flags=re.MULTILINE)
    
    return text

def generate_with_gemini(system_prompt, user_prompt, max_tokens=4000, temperature=0.6):
    """Generate content using Gemini API with system and user prompts"""
    try:
        model = get_gemini_model()
        
        # Combine system and user prompts for Gemini
        full_prompt = f"""System Instructions: {system_prompt}

User Request: {user_prompt}"""
        
        # Configure generation settings with enhanced parameters for more unique content
        generation_config = genai.types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
            top_p=0.95,  # Improved creativity and uniqueness
            top_k=40,    # Better variety in word choices
        )
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        raise e

# Template content based on Template1.pdf structure
# Company Research Configuration
SEARCH_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

TEMPLATE_CONTEXT = """
TalentCraft is a recruitment and talent acquisition company that helps businesses find top talent.

The marketing template should follow this EXACT ULTRA-SPECIFIC STRUCTURE:

**CRITICAL TEMPLATE ANALYSIS:**
Based on Template1 (MassMutual) and Template2 (ACV), the content must be:

1. **HYPER-SPECIFIC ROLE TARGETING:**
   - Use EXACT job titles from company's current openings (e.g., "Software Engineer III (Vehicle Intelligence)", "IT Project Manager")
   - Reference specific tech stacks mentioned in job posts ("Python, Java, Vue.js/React, AWS, microservices")
   - Include level indicators ("III", "II", "Senior", "Lead")

2. **INDUSTRY-SPECIFIC TERMINOLOGY:**
   - Use industry jargon that shows deep understanding
   - Reference specific business models ("digital marketplace", "B2B marketplaces", "Corporate Tech")
   - Include regulatory knowledge ("Colorado AI Act", "compliance frameworks")

3. **TECHNICAL DEPTH REQUIREMENTS:**
   - Mention specific technologies, platforms, and methodologies
   - Reference exact tools they use ("G-Suite/Okta", "Tableau, Power BI", "OpenAI API")
   - Include deployment specifics ("production-grade AI/ML", "microservices architecture")

4. **BUSINESS CONTEXT AWARENESS:**
   - Reference their specific business challenges ("scaling innovation", "feature rollouts")
   - Mention their growth stage and operational needs
   - Include timeline specifics ("within 30 days", "12-month contract")

5. **REASONS STRUCTURE (CRITICAL):**
   Each reason must include:
   - Specific role/department name
   - Technical requirements mentioned
   - "Why it matters:" section showing business impact
   - Industry-specific benefits
   - Exact timeframes and delivery methods

EXAMPLE QUALITY INDICATORS:
✅ "ACV's innovative digital marketplace relies heavily on backend and full-stack engineers with deep expertise in Python, Java, Vue.js/React, AWS, and microservices"
✅ "We supply developers with deep Python expertise, OpenAI API integration, and production-grade AI/ML deployment skills"
✅ "Your IT Admin II role requires a hybrid of technical troubleshooting, G-Suite/Okta administration"

❌ AVOID: Generic statements like "we provide great talent" or "experienced professionals"
❌ AVOID: Vague industry references
❌ AVOID: Non-specific technical mentions

The content should be tailored based on:
1. EXACT job titles and technical requirements from current openings
2. Specific technology stacks, tools, and platforms they use
3. Industry-specific challenges and regulatory requirements
4. Business model understanding and operational context
5. Growth stage, timeline pressures, and scaling challenges
6. Department-specific needs and team structures
"""

class CompanyResearcher:
    """Advanced company research engine for due diligence"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(SEARCH_HEADERS)
    
    def search_company_info(self, company_name, max_results=15):
        """Search for comprehensive company information using multiple targeted queries"""
        try:
            # Enhanced search queries with better diversity
            search_queries = [
                f'"{company_name}" company overview business',
                f'"{company_name}" headquarters location employees',
                f'"{company_name}" industry market revenue',
                f'"{company_name}" recent news 2024 2023',
                f'"{company_name}" hiring jobs recruiting',
                f'"{company_name}" technology stack software',
                f'"{company_name}" competitors market share',
                f'"{company_name}" about us company profile',
                f'{company_name} Inc CEO leadership team',
                f'{company_name} company size funding',
                # Added more diverse queries
                f'{company_name} company culture values',
                f'{company_name} products services offerings',
                f'{company_name} annual report financial',
                f'{company_name} press releases announcements',
                f'{company_name} careers job openings'
            ]
            
            all_results = []
            successful_queries = 0
            
            for i, query in enumerate(search_queries):
                try:
                    print(f"🔍 Search {i+1}/{len(search_queries)}: {query[:50]}...")
                    results = self._web_search(query, max_results=4)  # Increased from 3 to 4
                    if results:
                        all_results.extend(results)
                        successful_queries += 1
                        print(f"   ✅ Found {len(results)} results")
                    else:
                        print(f"   ⚠️ No results found")
                    
                    # Brief pause to avoid rate limiting
                    time.sleep(0.3)  # Reduced from 0.5 to 0.3
                    
                    # Early exit if we have enough diverse results
                    if len(all_results) > 60 and successful_queries >= 8:
                        print(f"📊 Early exit: {len(all_results)} raw results from {successful_queries} successful queries")
                        break
                    
                except Exception as e:
                    print(f"   ❌ Query failed: {str(e)}")
                    continue
            
            print(f"📊 Raw results collected: {len(all_results)}")
            
            # Remove duplicates based on content similarity
            unique_results = self._deduplicate_results(all_results)
            print(f"📊 After deduplication: {len(unique_results)} unique results")
            
            # Additional fallback: if still no results, try simpler searches
            if len(unique_results) == 0:
                print("🔄 No results found, trying fallback searches...")
                fallback_queries = [
                    f'{company_name}',
                    f'{company_name} company',
                    f'{company_name} business'
                ]
                
                for query in fallback_queries:
                    try:
                        fallback_results = self._web_search(query, max_results=5)
                        if fallback_results:
                            all_results.extend(fallback_results)
                    except:
                        continue
                
                unique_results = self._deduplicate_results(all_results)
                print(f"📊 After fallback: {len(unique_results)} unique results")
            
            return unique_results[:max_results]
            
        except Exception as e:
            print(f"Error in company search: {str(e)}")
            return []
    
    def _deduplicate_results(self, results):
        """Remove duplicate search results based on content similarity"""
        unique_results = []
        seen_snippets = set()
        seen_urls = set()
        
        for result in results:
            # Create a normalized version of the snippet for comparison
            snippet_normalized = result['snippet'].lower().strip()
            url_normalized = result.get('url', '').lower().strip()
            
            # Use a more sophisticated uniqueness check
            # 1. Check URL similarity (avoid same-page duplicates)
            # 2. Check content similarity with longer snippets for better differentiation
            snippet_key = snippet_normalized[:200]  # Increased from 100 to 200 chars
            url_key = url_normalized.split('?')[0]  # Remove query params for URL comparison
            
            # More lenient requirements:
            # - Reduced minimum snippet length from 50 to 30 chars
            # - Added URL-based deduplication as primary filter
            # - Only apply snippet deduplication if URL is not unique
            is_unique_url = url_key not in seen_urls
            is_unique_content = snippet_key not in seen_snippets
            has_sufficient_content = len(snippet_normalized) > 30
            
            if has_sufficient_content and (is_unique_url or is_unique_content):
                unique_results.append(result)
                seen_snippets.add(snippet_key)
                if url_key:
                    seen_urls.add(url_key)
        
        return unique_results
    
    def _web_search(self, query, max_results=10):
        """Perform web search using multiple methods for better results"""
        try:
            # Method 1: Try Google search via web scraping
            google_results = self._google_search(query, max_results=max_results//2)
            
            # Method 2: Try DuckDuckGo as backup
            ddg_results = self._duckduckgo_search(query, max_results=max_results//2)
            
            # Combine results - REMOVED second deduplication layer
            # The main deduplication will happen in _deduplicate_results()
            all_results = google_results + ddg_results
            
            # Simple filtering for obviously invalid results only
            valid_results = []
            for result in all_results:
                if (result.get('title') and result.get('snippet') and 
                    len(result['snippet'].strip()) > 20 and
                    len(result['title'].strip()) > 5):
                    valid_results.append(result)
            
            return valid_results[:max_results * 2]  # Return more results for better deduplication
            
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return []
    
    def _google_search(self, query, max_results=5):
        """Search Google for company information"""
        try:
            # Google search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&num={max_results}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(search_url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"   🔍 Google search returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract Google search results with better error handling
            search_containers = soup.find_all('div', class_='g')
            print(f"   🔍 Google found {len(search_containers)} search containers")
            
            for i, result in enumerate(search_containers[:max_results]):
                try:
                    # Find title
                    title_elem = result.find('h3')
                    if not title_elem:
                        continue
                    
                    # Find snippet with multiple fallback strategies
                    snippet_elem = (result.find('span', {'data-ved': True}) or 
                                   result.find('div', class_='VwiC3b') or
                                   result.find('div', class_='IsZvec') or 
                                   result.find('span', class_='aCOpRe') or
                                   result.find('div', class_='s') or
                                   result.find('span', class_='st'))
                    
                    if not snippet_elem:
                        # Last resort: look for any div with substantial text
                        all_divs = result.find_all('div')
                        for div in all_divs:
                            text = div.get_text().strip()
                            if len(text) > 50 and len(text) < 500:
                                snippet_elem = div
                                break
                    
                    # Find URL
                    url_elem = result.find('a')
                    url = url_elem.get('href', '') if url_elem else ''
                    
                    if title_elem and snippet_elem:
                        title_text = title_elem.get_text().strip()
                        snippet_text = snippet_elem.get_text().strip()
                        
                        if len(title_text) > 0 and len(snippet_text) > 10:
                            results.append({
                                'title': title_text,
                                'snippet': snippet_text,
                                'url': url,
                                'source': 'google'
                            })
                            
                except Exception as elem_error:
                    print(f"   ⚠️ Error processing Google result {i}: {str(elem_error)}")
                    continue
            
            print(f"   🔍 Google extracted {len(results)} valid results")
            return results
            
        except Exception as e:
            print(f"   ❌ Google search failed: {str(e)}")
            return []
    
    def _duckduckgo_search(self, query, max_results=5):
        """Backup search using DuckDuckGo"""
        try:
            # Use DuckDuckGo instant search API (more reliable)
            search_url = f"https://api.duckduckgo.com/?q={query.replace(' ', '+')}&format=json&no_html=1&skip_disambig=1"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                print(f"   🦆 DuckDuckGo API returned status {response.status_code}, trying HTML fallback")
                return self._duckduckgo_html_search(query, max_results)
            
            data = response.json()
            results = []
            
            # Extract results from different sections
            if 'RelatedTopics' in data and data['RelatedTopics']:
                print(f"   🦆 DuckDuckGo API found {len(data['RelatedTopics'])} related topics")
                for topic in data['RelatedTopics'][:max_results]:
                    if isinstance(topic, dict) and 'Text' in topic and 'FirstURL' in topic:
                        text = topic.get('Text', '')
                        if len(text) > 20:  # Ensure substantial content
                            results.append({
                                'title': text[:100] + ('...' if len(text) > 100 else ''),
                                'snippet': text,
                                'url': topic.get('FirstURL', ''),
                                'source': 'duckduckgo_api'
                            })
            
            # Add abstract if available
            if 'Abstract' in data and data['Abstract'] and len(data['Abstract']) > 20:
                results.insert(0, {
                    'title': data.get('Heading', query),
                    'snippet': data['Abstract'],
                    'url': data.get('AbstractURL', ''),
                    'source': 'duckduckgo_api'
                })
            
            print(f"   🦆 DuckDuckGo API extracted {len(results)} results")
            
            # If API didn't provide good results, try HTML fallback
            if len(results) == 0:
                print(f"   🦆 No API results, trying HTML fallback")
                return self._duckduckgo_html_search(query, max_results)
            
            return results[:max_results]
            
        except Exception as e:
            print(f"   ❌ DuckDuckGo API search failed: {str(e)}")
            return self._duckduckgo_html_search(query, max_results)
    
    def _duckduckgo_html_search(self, query, max_results=5):
        """Fallback HTML scraping for DuckDuckGo"""
        try:
            search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                print(f"   🦆 DuckDuckGo HTML returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            results = []
            
            # Extract search results
            result_containers = soup.find_all('div', class_='result')
            print(f"   🦆 DuckDuckGo HTML found {len(result_containers)} result containers")
            
            for i, result in enumerate(result_containers[:max_results]):
                try:
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem and snippet_elem:
                        title_text = title_elem.get_text().strip()
                        snippet_text = snippet_elem.get_text().strip()
                        
                        if len(title_text) > 0 and len(snippet_text) > 10:
                            results.append({
                                'title': title_text,
                                'snippet': snippet_text,
                                'url': title_elem.get('href', ''),
                                'source': 'duckduckgo_html'
                            })
                            
                except Exception as elem_error:
                    print(f"   ⚠️ Error processing DuckDuckGo result {i}: {str(elem_error)}")
                    continue
            
            print(f"   🦆 DuckDuckGo HTML extracted {len(results)} results")
            return results
            
        except Exception as e:
            print(f"   ❌ DuckDuckGo HTML search failed: {str(e)}")
            return []
    
    def analyze_company_data(self, company_name, search_results):
        """Analyze search results to extract key company insights"""
        try:
            # Combine all text from search results
            all_text = f"Company: {company_name}\n\n"
            for result in search_results:
                all_text += f"Title: {result['title']}\n"
                all_text += f"Content: {result['snippet']}\n\n"
            
            # Extract key information using text analysis
            insights = {
                'company_name': company_name,
                'industry': self._extract_industry(all_text),
                'company_size': self._extract_company_size(all_text),
                'recent_news': self._extract_recent_news(search_results),
                'challenges': self._extract_challenges(all_text),
                'competitors': self._extract_competitors(all_text),
                'key_facts': self._extract_key_facts(all_text)
            }
            
            return insights
            
        except Exception as e:
            print(f"Error analyzing company data: {str(e)}")
            return {'company_name': company_name, 'error': str(e)}
    
    def _extract_industry(self, text):
        """Extract industry information from text"""
        industry_keywords = {
            'technology': ['tech', 'software', 'saas', 'artificial intelligence', 'ai', 'machine learning', 'data science'],
            'healthcare': ['healthcare', 'medical', 'pharmaceutical', 'biotech', 'health'],
            'finance': ['financial', 'banking', 'fintech', 'investment', 'insurance'],
            'retail': ['retail', 'e-commerce', 'consumer', 'shopping'],
            'manufacturing': ['manufacturing', 'industrial', 'automotive', 'aerospace'],
            'consulting': ['consulting', 'advisory', 'professional services'],
            'media': ['media', 'advertising', 'marketing', 'entertainment']
        }
        
        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry.title()
        
        return "Not determined"
    
    def _extract_company_size(self, text):
        """Extract company size indicators from text"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['fortune 500', 'large corporation', 'multinational', 'global company']):
            return "Large Enterprise (1000+ employees)"
        elif any(term in text_lower for term in ['mid-size', 'medium', '100-1000 employees']):
            return "Mid-size Company (100-1000 employees)"
        elif any(term in text_lower for term in ['startup', 'small business', 'growing company']):
            return "Small to Medium Business (10-100 employees)"
        else:
            return "Size not determined"
    
    def _extract_recent_news(self, search_results):
        """Extract recent news and developments"""
        news_items = []
        for result in search_results:
            if any(term in result['title'].lower() for term in ['news', 'announces', 'launches', 'reports', 'hiring']):
                news_items.append(result['title'])
        
        return news_items[:3]  # Return top 3 news items
    
    def _extract_challenges(self, text):
        """Extract potential business challenges from text"""
        challenge_keywords = [
            'hiring difficulties', 'talent shortage', 'recruitment challenges',
            'skills gap', 'competitive market', 'growth challenges',
            'scaling issues', 'workforce expansion'
        ]
        
        text_lower = text.lower()
        found_challenges = []
        
        for challenge in challenge_keywords:
            if challenge in text_lower:
                found_challenges.append(challenge.title())
        
        return found_challenges
    
    def _extract_competitors(self, text):
        """Extract competitor information from text"""
        # This is a simplified version - in production, you'd want more sophisticated competitor detection
        competitor_patterns = [
            r'competes with ([A-Za-z\s,]+)',
            r'competitors include ([A-Za-z\s,]+)',
            r'rivals ([A-Za-z\s,]+)'
        ]
        
        competitors = []
        for pattern in competitor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                competitors.extend([comp.strip() for comp in match.split(',')])
        
        return competitors[:5]  # Return top 5 competitors
    
    def _extract_key_facts(self, text):
        """Extract key business facts and statistics"""
        facts = []
        
        # Look for revenue, funding, employee count, etc.
        revenue_pattern = r'\$[\d,.]+ (?:million|billion) (?:revenue|sales)'
        funding_pattern = r'\$[\d,.]+ (?:million|billion) (?:funding|investment)'
        employee_pattern = r'[\d,]+ employees'
        
        for pattern in [revenue_pattern, funding_pattern, employee_pattern]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            facts.extend(matches)
        
        return facts[:5]  # Return top 5 facts
    
    def scrape_company_website(self, url):
        """Scrape and analyze company website content"""
        try:
            if not url:
                return {}
            
            # Ensure URL has proper protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            print(f"🌐 Analyzing website: {url}")
            
            # Set a shorter timeout and user agent for website scraping
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = self.session.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract key information
            website_data = {
                'title': soup.title.string.strip() if soup.title else '',
                'meta_description': '',
                'main_content': '',
                'about_content': '',
                'services_content': '',
                'careers_content': '',
                'news_content': ''
            }
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                website_data['meta_description'] = meta_desc.get('content', '')
            
            # Get main content (first few paragraphs)
            paragraphs = soup.find_all('p')[:10]  # First 10 paragraphs
            main_text = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
            website_data['main_content'] = main_text[:1500]  # Limit to 1500 chars
            
            # Look for specific sections
            sections_to_find = {
                'about_content': ['about', 'about-us', 'company', 'our-story', 'who-we-are'],
                'services_content': ['services', 'products', 'solutions', 'what-we-do'],
                'careers_content': ['careers', 'jobs', 'join-us', 'work-with-us', 'team'],
                'news_content': ['news', 'blog', 'press', 'announcements', 'updates']
            }
            
            for content_type, keywords in sections_to_find.items():
                for keyword in keywords:
                    # Look for divs, sections, or links containing these keywords
                    elements = soup.find_all(['div', 'section', 'a'], class_=lambda x: x and keyword in x.lower())
                    if not elements:
                        elements = soup.find_all(['div', 'section'], id=lambda x: x and keyword in x.lower())
                    if not elements:
                        # Look for text containing these keywords
                        elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
                        if elements:
                            # Get parent elements
                            elements = [elem.parent for elem in elements[:3]]
                    
                    if elements:
                        content = ' '.join([elem.get_text().strip() for elem in elements[:3]])
                        if len(content) > 100:  # Only if we found substantial content
                            website_data[content_type] = content[:800]  # Limit content
                            break
            
            print(f"✅ Website analysis complete. Extracted {len(website_data['main_content'])} chars of content")
            return website_data
            
        except Exception as e:
            print(f"⚠️ Website scraping failed for {url}: {str(e)}")
            return {'error': f"Could not access website: {str(e)}"}

def research_and_generate_content(company_name, job_roles, company_url=None, company_context=None):
    """Research company and generate comprehensive marketing content"""
    
    try:
        # Initialize researcher
        researcher = CompanyResearcher()
        
        # Phase 1: Website Analysis (if URL provided)
        website_data = {}
        if company_url:
            print(f"🌐 Analyzing company website...")
            website_data = researcher.scrape_company_website(company_url)
        
        # Phase 2: Research company
        print(f"🔍 Researching {company_name}...")
        search_results = researcher.search_company_info(company_name)
        
        if not search_results:
            print(f"⚠️ Limited search results for {company_name}, proceeding with basic analysis")
        
        # Phase 2: Analyze research data
        print(f"📊 Analyzing company data...")
        company_insights = researcher.analyze_company_data(company_name, search_results)
        
        if 'error' in company_insights:
            print(f"⚠️ Analysis error: {company_insights['error']}")
        
        # Phase 3: Research industry and role-specific challenges (optional, don't fail if this fails)
        industry_results = []
        try:
            print(f"🏭 Researching industry trends...")
            industry_query = f"{company_insights.get('industry', company_name)} industry recruitment challenges hiring trends"
            industry_results = researcher.search_company_info(industry_query)
        except Exception as e:
            print(f"⚠️ Industry research failed: {str(e)}")
        
        # Phase 4: Generate enhanced content with research
        print(f"✍️ Generating personalized content...")
        content = generate_marketing_content_with_research(
            company_name, job_roles, company_insights, search_results, 
            website_data, company_context
        )
        
        # Validate content was generated successfully
        if not content or content.startswith("Error"):
            # Fallback to basic content generation
            print("⚠️ Enhanced generation failed, using fallback method")
            content = generate_fallback_content(company_name, job_roles, company_insights, website_data, company_context)
        
        return {
            'content': content,
            'research_insights': company_insights,
            'search_results_count': len(search_results),
            'industry_results_count': len(industry_results),
            'website_analyzed': bool(website_data and not website_data.get('error')),
            'website_data': website_data
        }
        
    except Exception as e:
        print(f"❌ Research pipeline failed: {str(e)}")
        
        # Generate fallback content with minimal research
        fallback_insights = {
            'company_name': company_name,
            'industry': 'Business Services',
            'company_size': 'Not determined',
            'recent_news': [],
            'challenges': ['Talent acquisition challenges'],
            'competitors': [],
            'key_facts': []
        }
        
        fallback_content = generate_fallback_content(company_name, job_roles, fallback_insights, {}, company_context)
        
        return {
            'content': fallback_content,
            'research_insights': fallback_insights,
            'search_results_count': 0,
            'research_error': str(e),
            'website_analyzed': False,
            'website_data': {}
        }

def generate_fallback_content(company_name, job_roles, company_insights, website_data=None, company_context=None):
    """Generate content when research fails or is limited"""
    
    fallback_prompt = f"""
    You are a marketing expert at TalentCraft, a recruitment company. Create professional marketing content for:
    
    Company: {company_name}
    Job Roles: {job_roles}
    Available Company Info: {company_insights.get('industry', 'General business')} industry
    
    Create a compelling but professional marketing proposal that includes:
    
    1. Brief professional introduction acknowledging {company_name} (1-2 sentences maximum)
    2. 5 detailed reasons why they should partner with TalentCraft for {job_roles} hiring (2-3 specific sentences each)
    3. Focus on specific recruitment challenges and TalentCraft's detailed solutions
    4. Include specific technical requirements, industry challenges, and concrete value propositions
    5. CRITICAL: Content must fit on ONE PAGE when formatted (approximately 400-500 words maximum)
    6. Keep introduction to 1-2 sentences maximum (40-60 words)
    7. Each reason should be 2-3 concise, specific sentences (60-80 words per reason maximum)
    
    TEXT FORMATTING REQUIREMENTS:
    - DO NOT use any markdown formatting characters (NO ** for bold, NO * for italics, NO # for headers)
    - Use plain text only - no special formatting characters
    - For emphasis, use capital letters or descriptive language instead of markdown
    - Write in a way that can be directly copied and pasted without cleanup
    - Use line breaks and spacing for visual organization instead of markdown
    - Use proper title case for section headings (not ALL CAPS)
    - Format numbered lists without any leading spaces or tabs - start text immediately after the number
    
    CONTENT FORMATTING REQUIREMENTS:
    - DO NOT include email subject lines (no "Subject:" lines)
    - DO NOT include formal email signatures or closings (no "Sincerely," "Best regards," etc.)
    - DO NOT include sender name or title at the end
    - Write as direct business proposal content, not as an email
    
    REASON TITLE GUIDELINES:
    - Do NOT use job position names as reason titles (avoid titles like "Software Engineers," "Data Scientists," "Product Managers")
    - Instead use strategic business-focused titles like "Accelerated Technical Innovation," "Competitive Talent Acquisition Advantage," "Market-Leading Expertise Access"
    - Keep titles to one complete sentence maximum but specific and impactful
    - Focus on the business value and strategic advantage each reason provides
    - Make titles compelling and outcome-focused rather than role-focused
    
    IMPORTANT: Write with complete confidence and authority. Demonstrate TalentCraft's premier status through:
    - Sophisticated language and authoritative positioning
    - Confident phrases like "established expertise," "proven methodologies," "recognized excellence"
    - Focus on quality of service and deep market understanding
    - Assertive statements about market conditions and business needs
    
    Write as if you have complete knowledge of their industry and business needs. Never use uncertain language.
    Make it compelling and authoritative while keeping it professional and focused on business value.
    """
    
    try:
        system_prompt = "You are a senior marketing strategist for TalentCraft, a premier recruitment firm. Write with complete authority and confidence, demonstrating deep market knowledge and expertise. Use sophisticated, assertive language that shows you fully understand the client's industry and business needs. Never use uncertain phrases or fabricate statistics - show expertise through confident analysis and positioning."
        
        content = generate_with_gemini(
            system_prompt=system_prompt,
            user_prompt=fallback_prompt,
            max_tokens=1200,  # Reduced for single-page documents
            temperature=0.8  # Higher temperature for more creative fallback content
        )
        
        # Post-process to remove any markdown formatting that might have slipped through
        content = clean_markdown_formatting(content)
        return content
    
    except Exception as e:
        return f"""
        {company_name} faces unique challenges in securing top-tier talent for {job_roles} positions. TalentCraft specializes in addressing these exact recruitment needs.
        
        Here's why leading companies partner with us:
        
        1. SPECIALIZED EXPERTISE: We understand the unique requirements for {job_roles} and have a proven track record of successful placements.
        
        2. EXTENSIVE NETWORK: Our talent network includes top-tier professionals specifically in your target roles.
        
        3. STREAMLINED PROCESS: We handle the entire recruitment process, saving your team valuable time and resources.
        
        4. QUALITY GUARANTEE: We ensure each candidate meets your exact specifications before presentation.
        
        5. ONGOING SUPPORT: Our partnership doesn't end with placement - we provide ongoing support to ensure long-term success.
        
        TalentCraft's proven methodologies and extensive industry network position us as the strategic partner {company_name} needs to secure exceptional {job_roles} talent efficiently and effectively.
        
        [Note: This is a fallback message due to technical limitations. For enhanced research-backed content, please try again.]
        """

def generate_marketing_content_with_research(company_name, job_roles, company_insights, search_results, website_data=None, company_context=None):
    """Generate marketing content enhanced with comprehensive research"""
    
    # Create detailed research summary for the prompt
    research_summary = f"""
    
    COMPREHENSIVE COMPANY RESEARCH FOR {company_name.upper()}:
    
    Industry: {company_insights.get('industry', 'Not determined')}
    Company Size: {company_insights.get('company_size', 'Not determined')}
    
    Recent News & Developments:
    {chr(10).join(f"- {news}" for news in company_insights.get('recent_news', [])) if company_insights.get('recent_news') else "- No recent news found"}
    
    Identified Business Challenges:
    {chr(10).join(f"- {challenge}" for challenge in company_insights.get('challenges', [])) if company_insights.get('challenges') else "- General market challenges apply"}
    
    Key Business Facts:
    {chr(10).join(f"- {fact}" for fact in company_insights.get('key_facts', [])) if company_insights.get('key_facts') else "- Research ongoing"}
    
    Competitors in Space:
    {chr(10).join(f"- {comp}" for comp in company_insights.get('competitors', [])) if company_insights.get('competitors') else "- Competitive landscape analysis needed"}
    
    Raw Research Data Summary:
    Total sources analyzed: {len(search_results)}
    Research confidence: {"High" if len(search_results) > 5 else "Medium" if len(search_results) > 2 else "Basic"}
    
    WEBSITE ANALYSIS:
    {f"Website analyzed: {website_data.get('title', 'N/A')}" if website_data and not website_data.get('error') else "No website provided or analysis failed"}
    {f"Company description: {website_data.get('meta_description', '')[:200]}..." if website_data and website_data.get('meta_description') else ""}
    {f"Services/Products: {website_data.get('services_content', '')[:300]}..." if website_data and website_data.get('services_content') else ""}
    {f"About company: {website_data.get('about_content', '')[:300]}..." if website_data and website_data.get('about_content') else ""}
    
    ADDITIONAL CONTEXT PROVIDED:
    {company_context if company_context else "No additional context provided"}
    """
    
    prompt = f"""
    You are a senior marketing strategist at TalentCraft, a premium recruitment firm. You've just completed extensive due diligence research on a prospect. Your task is to create a compelling, research-backed marketing proposal that demonstrates your thorough understanding of their business.
    
    TARGET COMPANY: {company_name}
    ROLES THEY'RE HIRING: {job_roles}
    
    {research_summary}
    
    {TEMPLATE_CONTEXT}
    
    Based on your comprehensive research, create a highly personalized marketing proposal that includes:
    
    1. RESEARCH-BACKED INTRODUCTION (1-2 sentences maximum)
       - Reference specific industry insights or recent developments
       - Demonstrate you understand their business context
       - Keep it brief and impactful for single-page format
    
    2. Five Strategic Reasons why {company_name} should partner with TalentCraft:
       
       Each reason must:
       - Be directly tied to your research findings
       - Address specific challenges their industry/size faces
       - Be SPECIFIC and DETAILED: 2-3 sentences per reason with concrete examples and specific value propositions
       - Highlight TalentCraft's specific expertise for their situation with detailed explanations
       - Include specific technical requirements, industry challenges, or business contexts
       - Have descriptive, business-focused titles (NOT just job position names)
       - Focus on business value and strategic advantages with specific examples
       - Format each numbered reason without any indentation or tab spaces - start text immediately after "1. " "2. " etc.
       - Start each reason with a compelling, specific title (one complete sentence maximum) followed by a colon, then detailed explanation
       - Keep reason titles impactful and specific - one sentence that captures the key business value
       - Balance specificity with page constraints - detailed but efficiently written
    
    CRITICAL FORMATTING REQUIREMENTS FOR SINGLE-PAGE DOCUMENT:
    - TOTAL CONTENT must fit on one page when formatted (approximately 400-500 words maximum)
    - Keep introduction to 1-2 sentences maximum (40-60 words)
    - Each reason should be 2-3 concise, specific sentences (60-80 words per reason maximum)
    - Be specific and impactful - include technical details, industry specifics, and concrete value propositions
    - Focus on the most compelling and detailed value propositions that demonstrate deep understanding
    - Write efficiently but with sufficient detail to be compelling and credible
    - Prioritize impact over length - every word must add value
    - CRITICAL: Reason titles must be one complete sentence maximum but specific and impactful
    
    CRITICAL REQUIREMENTS:
    - Use specific insights from your research throughout
    - Write with COMPLETE CONFIDENCE - you are a leading expert who has thoroughly researched this company
    - Reference industry trends and challenges with authority
    - Demonstrate deep market knowledge and business understanding
    - Make it clear this is a highly personalized, research-driven proposal
    - Professional yet engaging tone with confident authority
    - Focus on business impact and ROI with specific examples
    
    CONFIDENCE & TONE GUIDELINES:
    - NEVER use uncertain language like "limited data," "research ongoing," or "initial findings"
    - Write as if you have complete knowledge and understanding of their business
    - Use assertive phrases: "Our analysis shows," "We understand," "Your industry requires," "Market conditions indicate"
    - Avoid hedging language: NO "appears to be," "seems like," "might benefit"
    - Instead use direct statements: "is positioned," "requires," "will benefit"
    - Demonstrate authority through specific insights and confident recommendations
    
    STATISTICS & CREDIBILITY GUIDELINES:
    - NEVER make up specific statistics, numbers, or metrics (e.g., "placed 500+ professionals")
    - Instead, use compelling language that demonstrates premier status without false claims
    - Use phrases like "established track record," "proven expertise," "recognized leader"
    - Focus on qualitative excellence rather than quantitative claims you cannot verify
    - Demonstrate premium positioning through sophisticated language and approach
    - Show confidence through deep industry knowledge, not fabricated numbers
    
    TEXT FORMATTING REQUIREMENTS:
    - DO NOT use any markdown formatting characters (NO ** for bold, NO * for italics, NO # for headers)
    - Use plain text only - no special formatting characters
    - For emphasis, use capital letters or descriptive language instead of markdown
    - Write in a way that can be directly copied and pasted without cleanup
    - Use line breaks and spacing for visual organization instead of markdown
    - Use proper title case for section headings (not ALL CAPS)
    - Format numbered lists without any leading spaces or tabs - start text immediately after the number
    
    CONTENT FORMATTING REQUIREMENTS:
    - DO NOT include email subject lines (no "Subject:" lines)
    - DO NOT include formal email signatures or closings (no "Sincerely," "Best regards," etc.)
    - DO NOT include sender name or title at the end
    - Start directly with the business content
    - End with the value proposition or call to action
    - Write as direct business proposal content, not as an email
    
    REASON TITLE GUIDELINES:
    - Do NOT use job position names as reason titles (avoid titles like "Software Engineers," "Data Scientists," "Product Managers")
    - Instead use strategic business-focused titles like "Accelerated Technical Innovation," "Competitive Talent Acquisition Advantage," "Market-Leading Expertise Access"
    - Keep titles to one complete sentence maximum but specific and impactful
    - Focus on the business value and strategic advantage each reason provides
    - Make titles compelling and outcome-focused rather than role-focused
    """
    
    try:
        system_prompt = """You are a senior marketing strategist and research analyst at TalentCraft, a premier recruitment firm. You are recognized as an expert in your field with deep market knowledge and exceptional research capabilities. 

You specialize in creating highly personalized, research-driven business proposals that demonstrate authoritative market understanding and business insight. You write with complete confidence and authority, as you have thoroughly researched every aspect of the target company and understand their industry dynamics.

CRITICAL GUIDELINES:
- Write with absolute confidence and authority - never use uncertain language
- Demonstrate deep market knowledge through specific insights
- Position yourself as the definitive expert who fully understands their business
- NEVER fabricate statistics or metrics - show expertise through sophisticated analysis instead
- Use assertive, confident language that shows complete understanding
- Avoid any hedging or uncertain phrases - write with conviction"""
        
        content = generate_with_gemini(
            system_prompt=system_prompt,
            user_prompt=prompt,
            max_tokens=2000,  # Reduced for single-page documents
            temperature=0.7  # Slightly higher temperature for more unique research-based content
        )
        
        # Post-process to remove any markdown formatting that might have slipped through
        content = clean_markdown_formatting(content)
        return content
    
    except Exception as e:
        return f"Error generating enhanced content: {str(e)}"

@app.route('/')
def index():
    """Main page with the form"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    """Generate research-backed marketing content"""
    try:
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        company_url = data.get('company_url', '').strip()
        job_roles = data.get('job_roles', '').strip()
        company_context = data.get('company_context', '').strip()
        
        if not company_name or not job_roles:
            return jsonify({'error': 'Please provide both company name and job roles'}), 400
        
        # Research and generate enhanced content
        result = research_and_generate_content(company_name, job_roles, company_url, company_context)
        
        return jsonify({
            'success': True,
            'content': result['content'],
            'company_name': company_name,
            'job_roles': job_roles,
            'research_insights': result['research_insights'],
            'sources_analyzed': result['search_results_count'],
            'research_quality': "High" if result['search_results_count'] > 5 else "Medium" if result['search_results_count'] > 2 else "Basic"
        })
    
    except Exception as e:
        return jsonify({'error': f"Research and generation failed: {str(e)}"}), 500

@app.route('/generate-document', methods=['POST'])
def generate_document():
    """Generate and download a professionally formatted Word document"""
    try:
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        company_url = data.get('company_url', '').strip()
        job_roles = data.get('job_roles', '').strip()
        company_context = data.get('company_context', '').strip()
        content = data.get('content', '').strip()
        
        if not company_name or not job_roles:
            return jsonify({'error': 'Please provide both company name and job roles'}), 400
        
        # If content is not provided, generate it first
        if not content:
            result = research_and_generate_content(company_name, job_roles, company_url, company_context)
            content = result['content']
        
        # Generate the Word document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_company = re.sub(r'[^\w\s-]', '', company_name).strip()
        safe_company = re.sub(r'[-\s]+', '_', safe_company)
        filename = f"TalentCraft_Proposal_{safe_company}_{timestamp}.docx"
        
        # Create documents directory if it doesn't exist
        docs_dir = os.path.join(os.getcwd(), 'generated_documents')
        os.makedirs(docs_dir, exist_ok=True)
        
        # Generate the document
        output_path = os.path.join(docs_dir, filename)
        generate_marketing_document(
            marketing_content=content,
            company_name=company_name,
            job_roles=job_roles,
            output_filename=output_path
        )
        
        # Return the file for download
        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    except Exception as e:
        return jsonify({'error': f"Document generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    # Production configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)
