#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <stdexcept>
#include <string>

namespace modal
{

// ---------------------------------------------------------------------------
// Exception
//
// Exception is derived from std:exception, and is the base for a hierarchy
// of derived exception classes in Simpl.
class Exception : public std::exception {
    public:
        // Construct a new instance with the specified description.
        Exception(const std::string & str);

        // Destroy this Exception.
        virtual ~Exception(void) throw() {}

        // Return a description of this Exception in the form of a
        // C-style string (char pointer). Overrides std::exception::what.
        const char * what(void) const throw() {
            return _msg.c_str();
        }

        // Return a read-only refernce to this Exception's
        // description string.
        const std::string & str(void) const {
            return _msg;
        }

    protected:
        // string for storing the exception description
        std::string _msg;
};

} // end of namespace modal

#endif
