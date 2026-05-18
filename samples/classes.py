#  a class that prints details of the robot

#  class for Robot details
class Robot:

    # class has a constructor
    # class can have functions/MODELS
    def __init__(self, name, color, age):
        self.name = name
        self.color = color
        self.age = age

    # function to print the Robot details
    def introduce_self(self):
        print "My Name is: " + self.name
        print "My Color is: " + self.color
        print "My Age is: ", self.age
        print "==========================="

# class for mobile details
class Mobile:
    # constructor
    def __init__(self, color, brand, size, camera, isDualSim):
        self.color = color
        self.brand = brand
        self.size = size
        self.camera = camera
        self.isDualSim = isDualSim

    # function to print the mobile details
    def mobileDetails(self):
        print "Mobile Specs"
        print "Color: " + self.color
        print "Brand: " + self.brand
        print "Screen Size(inches): ", self.size
        print "Camera(megapixels): " + self.camera
        print "------------------------"

    def dualSim(self):
        self.isDualSim = True

    def notDualSim(self):
        self.isDualSim = False


# Creating an object
mob1 = Mobile("Black", "Apple", 5.7,"12 Megapixles", False)
mob2 = Mobile("Mid Night Blue", "Samsung", 6.0, "16 Megapixles", True)
mob3 = Mobile("White", "Google Pixel", 5.7,"16 Megapixles", True)
mob4 = Mobile("Space Gray", "Apple", 6.0,"12 Megapixles", True)

# function call to mobileDetails
mob1.mobileDetails()
mob2.mobileDetails()
mob3.mobileDetails()
mob4.mobileDetails()

# Creating an Object
r1 = Robot("Tom", "Blue", 40)
r2 = Robot("Steve", "Green", 50)

# function call to introduce_self
r1.introduce_self()
r2.introduce_self()


# lets say Mobile class owns the Robot class
# Accessing models from different classes
# Defining new attribute r1 in mob1
mob1.robotOwned = r1
mob1.robotOwned.introduce_self()
