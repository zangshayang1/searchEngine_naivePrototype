import pickle

class Term(object):
    def __init__(self, token, tf, init_position):
        self.token = token
        self.tf = tf
        self.positions = [init_position]

    def increment_tf(self):
        self.tf += 1
        return ;

    def append_newPosition(self, i):
        self.positions.append(i)
        return ;


t = Term('haha', 1, 1)

with open('test.json', 'wb') as f:
    pickle.dump(t, f)

with open('test.json', 'rb') as f:
    t = pickle.load(f)

print 'loaded. '

t.increment_tf()
print t.tf
