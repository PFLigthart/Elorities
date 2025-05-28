import json
import os
import random
import math
from datetime import datetime

class PriorityRanker:
    def __init__(self):
        self.themes_dir = "themes"
        self.ensure_themes_dir()
    
    def ensure_themes_dir(self):
        """Create themes directory if it doesn't exist"""
        if not os.path.exists(self.themes_dir):
            os.makedirs(self.themes_dir)
    
    def get_themes(self):
        """Get list of available themes"""
        themes = []
        if os.path.exists(self.themes_dir):
            files = os.listdir(self.themes_dir)
            items_files = [f for f in files if f.endswith('_items.json')]
            themes = [f.replace('_items.json', '') for f in items_files]
        return sorted(themes)
    
    def load_items(self, theme):
        """Load items for a theme"""
        items_file = os.path.join(self.themes_dir, f"{theme}_items.json")
        if os.path.exists(items_file):
            with open(items_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_items(self, theme, items):
        """Save items for a theme"""
        items_file = os.path.join(self.themes_dir, f"{theme}_items.json")
        with open(items_file, 'w') as f:
            json.dump(items, f, indent=2)
    
    def load_ratings(self, theme):
        """Load ratings for a theme"""
        ratings_file = os.path.join(self.themes_dir, f"{theme}_ratings.json")
        if os.path.exists(ratings_file):
            with open(ratings_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_ratings(self, theme, ratings):
        """Save ratings for a theme"""
        ratings_file = os.path.join(self.themes_dir, f"{theme}_ratings.json")
        with open(ratings_file, 'w') as f:
            json.dump(ratings, f, indent=2)
    
    def initialize_ratings(self, theme, items):
        """Initialize ratings for new items"""
        ratings = self.load_ratings(theme)
        updated = False
        
        for item in items:
            if item not in ratings:
                ratings[item] = {
                    "rating": 1000,
                    "plays": 0,
                    "wins": 0,
                    "losses": 0,
                    "date_added": datetime.now().isoformat(),
                    "biggest_win": 0,
                    "lowest_loss": 0
                }
                updated = True
        
        if updated:
            self.save_ratings(theme, ratings)
        return ratings
    
    def calculate_elo_change(self, winner_rating, loser_rating, k=32):
        """Calculate ELO rating change"""
        expected_winner = 1 / (1 + math.pow(10, (loser_rating - winner_rating) / 400))
        expected_loser = 1 / (1 + math.pow(10, (winner_rating - loser_rating) / 400))
        
        winner_change = k * (1 - expected_winner)
        loser_change = k * (0 - expected_loser)
        
        return winner_change, loser_change
    
    def update_ratings(self, theme, winner, loser):
        """Update ELO ratings after a match"""
        ratings = self.load_ratings(theme)
        
        winner_rating = ratings[winner]["rating"]
        loser_rating = ratings[loser]["rating"]
        
        winner_change, loser_change = self.calculate_elo_change(winner_rating, loser_rating)
        
        # Update ratings
        ratings[winner]["rating"] += winner_change
        ratings[loser]["rating"] += loser_change
        
        # Update stats
        ratings[winner]["plays"] += 1
        ratings[winner]["wins"] += 1
        ratings[loser]["plays"] += 1
        ratings[loser]["losses"] += 1
        
        # Track biggest win/loss
        if winner_change > ratings[winner]["biggest_win"]:
            ratings[winner]["biggest_win"] = winner_change
        if abs(loser_change) > ratings[loser]["lowest_loss"]:
            ratings[loser]["lowest_loss"] = abs(loser_change)
        
        self.save_ratings(theme, ratings)
    
    def create_theme(self):
        """Create a new theme"""
        print("\n--- Create New Theme ---")
        theme_name = input("Enter theme name: ").strip().lower()
        
        if not theme_name:
            print("Theme name cannot be empty!")
            return
        
        if theme_name in self.get_themes():
            print(f"Theme '{theme_name}' already exists!")
            return
        
        # Create empty files
        self.save_items(theme_name, [])
        self.save_ratings(theme_name, {})
        
        print(f"Theme '{theme_name}' created successfully!")
        
        # Ask if they want to add items now
        add_items = input("Add items now? (y/n): ").strip().lower()
        if add_items == 'y':
            self.add_items_to_theme(theme_name)
    
    def add_items_to_theme(self, theme):
        """Add items to an existing theme"""
        print(f"\n--- Add Items to '{theme}' ---")
        print("Enter items (one per line, empty line to finish):")
        
        items = self.load_items(theme)
        new_items = []
        
        while True:
            item = input("> ").strip()
            if not item:
                break
            if len(item) > 100:
                print("Item too long (max 100 characters)!")
                continue
            if item in items:
                print("Item already exists!")
                continue
            
            new_items.append(item)
            items.append(item)
        
        if new_items:
            self.save_items(theme, items)
            self.initialize_ratings(theme, items)
            print(f"Added {len(new_items)} items to '{theme}'")
        else:
            print("No items added.")
    
    def ranking_mode(self, theme):
        """Enter ranking mode for a theme"""
        items = self.load_items(theme)
        
        if len(items) < 2:
            print(f"Need at least 2 items in '{theme}' to start ranking!")
            return
        
        ratings = self.initialize_ratings(theme, items)
        
        print(f"\n--- Ranking Mode: {theme} ---")
        print("Use '<' to choose left item, '>' to choose right item, 'q' to quit")
        print()
        
        while True:
            # Pick two random distinct items
            item1, item2 = random.sample(items, 2)
            
            print(f"Which is more important/better?")
            print(f"  <  {item1}")
            print(f"  >  {item2}")
            print()
            
            choice = input("Your choice (</>): ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '<':
                self.update_ratings(theme, item1, item2)
                print(f"'{item1}' wins!\n")
            elif choice == '>':
                self.update_ratings(theme, item2, item1)
                print(f"'{item2}' wins!\n")
            else:
                print("Invalid choice! Use '<', '>', or 'q'\n")
    
    def view_rankings(self, theme):
        """View current rankings for a theme"""
        items = self.load_items(theme)
        ratings = self.load_ratings(theme)
        
        if not items:
            print(f"No items in '{theme}'!")
            return
        
        print(f"\n--- Rankings: {theme} ---")
        
        # Sort items by rating
        sorted_items = []
        for item in items:
            if item in ratings:
                sorted_items.append((item, ratings[item]["rating"]))
            else:
                sorted_items.append((item, 1000))
        
        sorted_items.sort(key=lambda x: x[1], reverse=True)
        
        if not sorted_items:
            print("No rankings available!")
            return
        
        # Normalize dash count based on ratings
        max_rating = sorted_items[0][1]
        min_rating = sorted_items[-1][1] if len(sorted_items) > 1 else max_rating
        rating_range = max_rating - min_rating if max_rating != min_rating else 1
        
        for i, (item, rating) in enumerate(sorted_items):
            # Calculate dash count (1-50 dashes)
            if rating_range > 0:
                dash_count = int(1 + 49 * (rating - min_rating) / rating_range)
            else:
                dash_count = 50
            
            dashes = "-" * dash_count
            
            print(f"{i+1:2}. {item}")
            print(f"    {dashes} ({rating:.0f})")
            
            # Show stats if available
            if item in ratings:
                stats = ratings[item]
                if stats["plays"] > 0:
                    print(f"    Plays: {stats['plays']}, Wins: {stats['wins']}, Losses: {stats['losses']}")
            print()
    
    def show_main_menu(self):
        """Display main menu"""
        themes = self.get_themes()
        
        print("\n=== Priority Ranker ===")
        print("\nAvailable themes:")
        
        if themes:
            for i, theme in enumerate(themes, 1):
                item_count = len(self.load_items(theme))
                print(f"  {i}. {theme} ({item_count} items)")
        else:
            print("  No themes available")
        
        print(f"\n  {len(themes) + 1}. Create new theme")
        print(f"  {len(themes) + 2}. Add items to existing theme")
        print(f"  {len(themes) + 3}. View rankings")
        print(f"  {len(themes) + 4}. Exit")
        
        return themes
    
    def run(self):
        """Main application loop"""
        while True:
            themes = self.show_main_menu()
            
            try:
                choice = input(f"\nEnter choice (1-{len(themes) + 4}): ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(themes):
                    # Selected a theme for ranking
                    selected_theme = themes[choice_num - 1]
                    self.ranking_mode(selected_theme)
                
                elif choice_num == len(themes) + 1:
                    # Create new theme
                    self.create_theme()
                
                elif choice_num == len(themes) + 2:
                    # Add items to existing theme
                    if not themes:
                        print("No themes available! Create a theme first.")
                        continue
                    
                    print("\nSelect theme to add items to:")
                    for i, theme in enumerate(themes, 1):
                        print(f"  {i}. {theme}")
                    
                    theme_choice = input("Enter theme number: ").strip()
                    theme_num = int(theme_choice)
                    
                    if 1 <= theme_num <= len(themes):
                        self.add_items_to_theme(themes[theme_num - 1])
                    else:
                        print("Invalid theme selection!")
                
                elif choice_num == len(themes) + 3:
                    # View rankings
                    if not themes:
                        print("No themes available! Create a theme first.")
                        continue
                    
                    print("\nSelect theme to view rankings:")
                    for i, theme in enumerate(themes, 1):
                        print(f"  {i}. {theme}")
                    
                    theme_choice = input("Enter theme number: ").strip()
                    theme_num = int(theme_choice)
                    
                    if 1 <= theme_num <= len(themes):
                        self.view_rankings(themes[theme_num - 1])
                    else:
                        print("Invalid theme selection!")
                
                elif choice_num == len(themes) + 4:
                    # Exit
                    print("Goodbye!")
                    break
                
                else:
                    print("Invalid choice!")
            
            except ValueError:
                print("Please enter a valid number!")
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break

if __name__ == "__main__":
    ranker = PriorityRanker()
    ranker.run()
