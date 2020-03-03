@objc public enum LogLevel : Int {
    case debug       = 0
    case verbose     = 1
    case info        = 5
    case application = 10
    case warning     = 15
    case error       = 20
    
    public func name() -> String {
        var readableName: String
        switch (self) {
        case .debug:
            readableName = "D"
        case .verbose:
            readableName = "V"
        case .info:
            readableName = "I"
        case .application:
            readableName = "A"
        case .warning:
            readableName = "W"
        case .error:
            readableName = "E"
        }
        return readableName
    }
}
