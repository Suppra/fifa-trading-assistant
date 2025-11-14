"""
Script de Ejemplo: Configuración de Alertas Personalizadas
Demuestra cómo usar el sistema de notificaciones Windows
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.windows_notifications import get_notifier
from app.models.database import DatabaseManager
from datetime import datetime


def test_all_notifications():
    """Test all notification types"""
    print("🧪 Testing Windows Notifications System\n")
    
    notifier = get_notifier()
    
    if not notifier.is_enabled():
        print("❌ Notifications not available. Install win10toast:")
        print("   pip install win10toast")
        return
    
    print("✅ Notifier initialized\n")
    
    # 1. Test notification
    print("1️⃣ Basic test notification...")
    notifier.test_notification()
    time.sleep(3)
    
    # 2. Price drop alert
    print("2️⃣ Price drop alert...")
    notifier.notify_price_drop(
        player_name="Kylian Mbappé",
        old_price=250000,
        new_price=235000,
        drop_pct=6.0
    )
    time.sleep(3)
    
    # 3. Price spike alert
    print("3️⃣ Price spike alert...")
    notifier.notify_price_spike(
        player_name="Erling Haaland",
        old_price=180000,
        new_price=198000,
        spike_pct=10.0
    )
    time.sleep(3)
    
    # 4. ROI milestone
    print("4️⃣ ROI milestone alert...")
    notifier.notify_roi_milestone(
        portfolio_roi=12.5,
        total_profit=85000
    )
    time.sleep(3)
    
    # 5. LSTM prediction
    print("5️⃣ LSTM prediction alert...")
    notifier.notify_lstm_prediction(
        player_name="Vinicius Jr",
        current_price=220000,
        predicted_price=242000,
        days=3
    )
    time.sleep(3)
    
    # 6. Peak hours
    print("6️⃣ Peak hours alert...")
    notifier.notify_peak_hours(
        action="COMPRAR",
        time_window="02:00-05:00",
        savings_or_profit=8.5
    )
    time.sleep(3)
    
    # 7. SBC detection
    print("7️⃣ SBC detection alert...")
    notifier.notify_sbc_requirement(
        sbc_name="Prime Icon Pack",
        required_rating=84,
        required_cards=11
    )
    time.sleep(3)
    
    # 8. Inventory warning
    print("8️⃣ Inventory warning...")
    notifier.notify_inventory_full(
        total_items=85,
        total_value=1250000
    )
    time.sleep(3)
    
    # 9. Profit target
    print("9️⃣ Profit target alert...")
    notifier.notify_profit_target(
        player_name="Jude Bellingham",
        buy_price=150000,
        sell_price=175000,
        profit=25000
    )
    time.sleep(3)
    
    # 10. Market trend
    print("🔟 Market trend alert...")
    notifier.notify_market_trend(
        trend_type="ALCISTA",
        avg_change_pct=4.2
    )
    
    print("\n✅ All notification tests completed!")


def demo_price_monitoring():
    """Demo: Monitor prices and send alerts"""
    print("📊 Demo: Price Monitoring with Alerts\n")
    
    notifier = get_notifier()
    
    if not notifier.is_enabled():
        print("❌ Notifications disabled")
        return
    
    try:
        db_manager = DatabaseManager()
        session = db_manager.get_session()
        
        # Get top players
        players = session.query(db_manager.Player).filter(
            db_manager.Player.rating >= 85
        ).limit(5).all()
        
        print(f"Monitoring {len(players)} players for price changes...\n")
        
        for player in players:
            # Get recent price history
            price_history = session.query(db_manager.PriceHistory).filter_by(
                player_id=player.player_id
            ).order_by(db_manager.PriceHistory.timestamp.desc()).limit(2).all()
            
            if len(price_history) >= 2:
                current_price = price_history[0].price
                previous_price = price_history[1].price
                
                change_pct = ((current_price - previous_price) / previous_price) * 100
                
                print(f"📌 {player.name} (Rating {player.rating})")
                print(f"   Previous: {previous_price:,} → Current: {current_price:,}")
                print(f"   Change: {change_pct:+.1f}%")
                
                # Alert on significant changes
                if change_pct <= -5:
                    print("   🔔 ALERT: Price dropped significantly!")
                    notifier.notify_price_drop(
                        player_name=player.name,
                        old_price=previous_price,
                        new_price=current_price,
                        drop_pct=abs(change_pct)
                    )
                    time.sleep(2)
                elif change_pct >= 8:
                    print("   🔔 ALERT: Price spiked!")
                    notifier.notify_price_spike(
                        player_name=player.name,
                        old_price=previous_price,
                        new_price=current_price,
                        spike_pct=change_pct
                    )
                    time.sleep(2)
                
                print()
        
        session.close()
        print("✅ Price monitoring demo completed")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_roi_tracking():
    """Demo: Track portfolio ROI and alert on milestones"""
    print("💼 Demo: Portfolio ROI Tracking\n")
    
    notifier = get_notifier()
    
    if not notifier.is_enabled():
        print("❌ Notifications disabled")
        return
    
    # Simulate portfolio growth
    print("Simulating portfolio growth over time...\n")
    
    initial_investment = 500000
    milestones = [5, 10, 15, 20]
    notified_milestones = set()
    
    for day in range(1, 31):
        # Simulate daily growth (0.5% average)
        current_value = initial_investment * (1 + 0.005 * day)
        profit = current_value - initial_investment
        roi = (profit / initial_investment) * 100
        
        print(f"Day {day}: Investment {initial_investment:,} → Value {current_value:,.0f} (ROI: {roi:+.1f}%)")
        
        # Check for milestone alerts
        for milestone in milestones:
            if roi >= milestone and milestone not in notified_milestones:
                print(f"   🎉 MILESTONE REACHED: {milestone}% ROI!")
                notifier.notify_roi_milestone(
                    portfolio_roi=roi,
                    total_profit=int(profit)
                )
                notified_milestones.add(milestone)
                time.sleep(2)
        
        time.sleep(0.5)  # Slow down simulation
    
    print(f"\n✅ Final ROI: {roi:+.1f}%")
    print(f"✅ Milestones reached: {sorted(notified_milestones)}")


def demo_peak_hours_alerts():
    """Demo: Peak hours monitoring"""
    print("⏰ Demo: Peak Hours Alerts\n")
    
    notifier = get_notifier()
    
    if not notifier.is_enabled():
        print("❌ Notifications disabled")
        return
    
    # Simulate different hours of the day
    scenarios = [
        {"hour": 3, "action": "COMPRAR", "window": "02:00-05:00", "metric": 7.5},
        {"hour": 10, "action": "ESPERAR", "window": "09:00-12:00", "metric": 2.0},
        {"hour": 20, "action": "VENDER", "window": "19:00-22:00", "metric": 9.2}
    ]
    
    print("Testing peak hours recommendations at different times:\n")
    
    for scenario in scenarios:
        print(f"⏰ {scenario['hour']}:00 - Action: {scenario['action']}")
        
        if scenario['action'] != "ESPERAR":
            notifier.notify_peak_hours(
                action=scenario['action'],
                time_window=scenario['window'],
                savings_or_profit=scenario['metric']
            )
            time.sleep(3)
        
        print()
    
    print("✅ Peak hours demo completed")


def configure_custom_alerts():
    """Example: Configure custom alert thresholds"""
    print("⚙️ Custom Alert Configuration\n")
    
    # Example configuration
    config = {
        'price_alerts': {
            'drop_threshold': 5.0,      # Alert on 5%+ drops
            'spike_threshold': 8.0,     # Alert on 8%+ spikes
            'watchlist': [
                'Kylian Mbappé',
                'Erling Haaland', 
                'Vinicius Jr',
                'Jude Bellingham'
            ]
        },
        'roi_milestones': [5, 10, 15, 20, 25, 30],
        'inventory_warnings': {
            'warning_level': 80,        # Alert at 80 items
            'critical_level': 90        # Urgent at 90 items
        },
        'profit_targets': {
            'quick_flip': 5,            # 5% for quick flips
            'normal_trade': 12,         # 12% for normal trades
            'long_term': 20             # 20% for investments
        },
        'notification_hours': {
            'start': 8,                 # Start at 8 AM
            'end': 23                   # End at 11 PM
        }
    }
    
    print("📋 Alert Configuration:")
    print(f"   Price Drop Threshold: {config['price_alerts']['drop_threshold']}%")
    print(f"   Price Spike Threshold: {config['price_alerts']['spike_threshold']}%")
    print(f"   Watchlist: {len(config['price_alerts']['watchlist'])} players")
    print(f"   ROI Milestones: {config['roi_milestones']}")
    print(f"   Inventory Warning: {config['inventory_warnings']['warning_level']} items")
    print(f"   Profit Targets: {config['profit_targets']}")
    print(f"   Active Hours: {config['notification_hours']['start']}:00 - {config['notification_hours']['end']}:00")
    
    return config


def main():
    """Main menu"""
    print("=" * 60)
    print("🔔 WINDOWS NOTIFICATIONS - DEMO & TESTING")
    print("=" * 60)
    print()
    
    while True:
        print("\nSelect an option:")
        print("1. Test all notification types")
        print("2. Demo: Price monitoring with alerts")
        print("3. Demo: Portfolio ROI tracking")
        print("4. Demo: Peak hours alerts")
        print("5. Show custom configuration example")
        print("0. Exit")
        
        choice = input("\nYour choice: ").strip()
        
        if choice == "1":
            test_all_notifications()
        elif choice == "2":
            demo_price_monitoring()
        elif choice == "3":
            demo_roi_tracking()
        elif choice == "4":
            demo_peak_hours_alerts()
        elif choice == "5":
            configure_custom_alerts()
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()
