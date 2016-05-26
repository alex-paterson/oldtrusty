def test(function, s):
    print "\n*** Testing {} ***".format(function.__name__)
    try:
        function(s)
    except ValueError as e:
        print "{} failed:".format(function.__name__), e
    raw_input("\nPress any key for next test")
