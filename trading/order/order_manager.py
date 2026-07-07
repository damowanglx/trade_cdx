"""
订单管理模块
管理订单状态、类型、执行
"""

from datetime import datetime
import uuid


class Order:
    """订单类"""
    
    def __init__(self, symbol, quantity, price, order_type='limit', direction='buy'):
        self.order_id = str(uuid.uuid4())[:8]
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.order_type = order_type
        self.direction = direction
        self.status = 'pending'
        self.created_at = datetime.now()
        self.executed_at = None
        self.executed_price = None
        self.executed_quantity = None
        self.commission = 0
        self.slippage = 0
        
    def execute(self, executed_price, executed_quantity=None):
        self.status = 'executed'
        self.executed_at = datetime.now()
        self.executed_price = executed_price
        self.executed_quantity = executed_quantity or self.quantity
        
        if self.direction == 'buy':
            self.slippage = (executed_price - self.price) / self.price
        else:
            self.slippage = (self.price - executed_price) / self.price
        
        trade_amount = self.executed_price * self.executed_quantity
        self.commission = trade_amount * 0.001
        
    def cancel(self):
        self.status = 'cancelled'
        
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price': self.price,
            'order_type': self.order_type,
            'direction': self.direction,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'executed_price': self.executed_price,
            'executed_quantity': self.executed_quantity,
            'commission': self.commission,
            'slippage': self.slippage,
        }


class OrderManager:
    """订单管理器"""
    
    def __init__(self):
        self.orders = []
        self.executed_orders = []
        
    def create_order(self, symbol, quantity, price, order_type='limit', direction='buy'):
        order = Order(symbol, quantity, price, order_type, direction)
        self.orders.append(order)
        return order
        
    def execute_order(self, order, executed_price):
        order.execute(executed_price)
        self.executed_orders.append(order)
        return order
        
    def cancel_order(self, order):
        order.cancel()
        return order
        
    def get_pending_orders(self):
        return [o for o in self.orders if o.status == 'pending']
        
    def get_executed_orders(self):
        return self.executed_orders
        
    def get_order_history(self):
        return [o.to_dict() for o in self.orders]
        
    def calculate_trade_stats(self):
        if not self.executed_orders:
            return {}
        
        total_commission = sum(o.commission for o in self.executed_orders)
        total_slippage = sum(o.slippage for o in self.executed_orders)
        
        buy_orders = [o for o in self.executed_orders if o.direction == 'buy']
        sell_orders = [o for o in self.executed_orders if o.direction == 'sell']
        
        return {
            'total_orders': len(self.executed_orders),
            'buy_orders': len(buy_orders),
            'sell_orders': len(sell_orders),
            'total_commission': total_commission,
            'total_slippage': total_slippage,
            'avg_slippage': total_slippage / len(self.executed_orders) if self.executed_orders else 0,
        }
